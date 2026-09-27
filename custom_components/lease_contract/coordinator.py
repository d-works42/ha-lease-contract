"""Coordinator for a single lease contract config entry.

Unlike a typical polling DataUpdateCoordinator, this one has no polling
interval. It recomputes its data whenever the configured odometer entity
reports a new state, via ``async_track_state_change_event``.
"""
from __future__ import annotations

import logging
from datetime import date

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .calculations import ContractResult, compute_contract_result
from .const import (
    CONF_END_DATE,
    CONF_MAX_KM,
    CONF_ODOMETER_ENTITY,
    CONF_START_DATE,
    CONF_START_ODOMETER,
    DOMAIN,
    STORE_KEY_MONTH_KEY,
    STORE_KEY_MONTH_START_ODOMETER,
    STORE_KEY_START_ODOMETER,
)
from .storage import LeaseContractStore

_LOGGER = logging.getLogger(__name__)


class LeaseContractCoordinator(DataUpdateCoordinator[ContractResult]):
    """Holds the computed state for one lease contract."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}-{entry.entry_id}", update_interval=None)
        self.entry = entry
        self.store = LeaseContractStore(hass, entry.entry_id)
        self._unsub_state_change = None

    # --- convenience accessors for the config entry data ---

    @property
    def odometer_entity_id(self) -> str:
        return self.entry.data[CONF_ODOMETER_ENTITY]

    @property
    def start_date(self) -> date:
        return dt_util.parse_date(self.entry.data[CONF_START_DATE])

    @property
    def end_date(self) -> date:
        return dt_util.parse_date(self.entry.data[CONF_END_DATE])

    @property
    def max_km(self) -> float:
        return float(self.entry.data[CONF_MAX_KM])

    # --- lifecycle ---

    async def async_setup(self) -> None:
        """Load storage, establish the baseline odometer reading, and subscribe."""
        await self.store.async_load()

        if STORE_KEY_START_ODOMETER not in self.store.data:
            manual_start = self.entry.data.get(CONF_START_ODOMETER)
            if manual_start is not None:
                baseline = float(manual_start)
            else:
                baseline = self._read_odometer_state() or 0.0
            self.store.data[STORE_KEY_START_ODOMETER] = baseline
            await self.store.async_save()

        self._unsub_state_change = async_track_state_change_event(
            self.hass, [self.odometer_entity_id], self._handle_odometer_event
        )

        await self.async_refresh()

    async def async_unload(self) -> None:
        """Undo the state-change subscription."""
        if self._unsub_state_change is not None:
            self._unsub_state_change()
            self._unsub_state_change = None

    @callback
    def _handle_odometer_event(self, event: Event[EventStateChangedData]) -> None:
        """Odometer entity produced a new state -> recompute."""
        self.hass.async_create_task(self.async_refresh())

    # --- data update ---

    def _read_odometer_state(self) -> float | None:
        state = self.hass.states.get(self.odometer_entity_id)
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE, ""):
            return None
        try:
            return float(state.state)
        except ValueError:
            _LOGGER.warning(
                "Odometer entity %s has a non-numeric state: %s",
                self.odometer_entity_id,
                state.state,
            )
            return None

    async def _async_update_data(self) -> ContractResult:
        current_odometer = self._read_odometer_state()

        if current_odometer is None:
            # Entity unavailable/unknown right now: keep the last good value if we
            # have one, otherwise fall back to the stored baseline.
            if self.data is not None:
                return self.data
            current_odometer = self.store.data.get(STORE_KEY_START_ODOMETER, 0.0)

        today = dt_util.now().date()
        month_key = f"{today.year}-{today.month:02d}"
        if self.store.data.get(STORE_KEY_MONTH_KEY) != month_key:
            self.store.data[STORE_KEY_MONTH_KEY] = month_key
            self.store.data[STORE_KEY_MONTH_START_ODOMETER] = current_odometer
            await self.store.async_save()

        return compute_contract_result(
            start_date=self.start_date,
            end_date=self.end_date,
            max_km=self.max_km,
            start_odometer=self.store.data[STORE_KEY_START_ODOMETER],
            current_odometer=current_odometer,
            month_start_odometer=self.store.data.get(
                STORE_KEY_MONTH_START_ODOMETER, current_odometer
            ),
            today=today,
        )
