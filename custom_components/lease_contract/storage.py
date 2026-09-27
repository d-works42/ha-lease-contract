"""Small persistence layer for per-contract baseline data.

We need to remember, across Home Assistant restarts:
  * the odometer reading that counts as "km 0" for this contract
  * the odometer reading at the start of the current calendar month

This uses Home Assistant's built-in Store helper (simple JSON on disk),
one file per config entry.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_VERSION


class LeaseContractStore:
    """Thin wrapper around a per-entry Store."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_{entry_id}")
        self.data: dict = {}

    async def async_load(self) -> None:
        """Load stored data from disk (or start empty)."""
        self.data = await self._store.async_load() or {}

    async def async_save(self) -> None:
        """Persist current data to disk."""
        await self._store.async_save(self.data)
