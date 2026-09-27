"""Services for the Lease Contract integration.

Provides `lease_contract.set_baseline`, letting the user manually correct
the stored baseline odometer reading(s) for a contract - e.g. when the
integration was set up mid-month (or mid-contract) and the automatically
captured baseline doesn't reflect the real reading at that point in time.
"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    ATTR_MONTH_START_ODOMETER,
    ATTR_START_ODOMETER,
    DOMAIN,
    SERVICE_SET_BASELINE,
    STORE_KEY_MONTH_START_ODOMETER,
    STORE_KEY_START_ODOMETER,
)

_LOGGER = logging.getLogger(__name__)

SET_BASELINE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_START_ODOMETER): vol.Coerce(float),
        vol.Optional(ATTR_MONTH_START_ODOMETER): vol.Coerce(float),
    }
)


def async_setup_services(hass: HomeAssistant) -> None:
    """Register integration-wide services (idempotent)."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_BASELINE):
        return

    async def _handle_set_baseline(call: ServiceCall) -> None:
        start_value = call.data.get(ATTR_START_ODOMETER)
        month_value = call.data.get(ATTR_MONTH_START_ODOMETER)

        if start_value is None and month_value is None:
            _LOGGER.warning(
                "lease_contract.set_baseline called without start_odometer or "
                "month_start_odometer - nothing to do"
            )
            return

        device_registry = dr.async_get(hass)
        entries = hass.data.get(DOMAIN, {})

        for device_id in call.data[ATTR_DEVICE_ID]:
            device = device_registry.async_get(device_id)
            if device is None:
                _LOGGER.warning("Unknown device_id %s", device_id)
                continue

            for entry_id in device.config_entries:
                coordinator = entries.get(entry_id)
                if coordinator is None:
                    continue  # device belongs to a different integration

                if start_value is not None:
                    coordinator.store.data[STORE_KEY_START_ODOMETER] = start_value
                if month_value is not None:
                    coordinator.store.data[STORE_KEY_MONTH_START_ODOMETER] = month_value

                await coordinator.store.async_save()
                await coordinator.async_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_SET_BASELINE, _handle_set_baseline, schema=SET_BASELINE_SCHEMA
    )
