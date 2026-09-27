"""Config flow for the Lease Contract integration."""
from __future__ import annotations

from datetime import date
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_END_DATE,
    CONF_MAX_KM,
    CONF_ODOMETER_ENTITY,
    CONF_START_DATE,
    CONF_START_ODOMETER,
    DOMAIN,
)

CONF_NAME = "name"


class LeaseContractConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup of a single car lease contract."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            start = user_input[CONF_START_DATE]
            end = user_input[CONF_END_DATE]
            if isinstance(start, str):
                start = date.fromisoformat(start)
            if isinstance(end, str):
                end = date.fromisoformat(end)

            if end <= start:
                errors["base"] = "end_before_start"
            else:
                await self.async_set_unique_id(user_input[CONF_ODOMETER_ENTITY])
                self._abort_if_unique_id_configured()

                data = dict(user_input)
                data[CONF_START_DATE] = start.isoformat()
                data[CONF_END_DATE] = end.isoformat()
                title = user_input.get(CONF_NAME) or "Car Lease"

                return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Car Lease"): str,
                vol.Required(CONF_ODOMETER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_MAX_KM): vol.Coerce(float),
                vol.Required(CONF_START_DATE): selector.DateSelector(),
                vol.Required(CONF_END_DATE): selector.DateSelector(),
                vol.Optional(CONF_START_ODOMETER): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
