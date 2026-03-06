"""Cycle Tracker – Config Flow."""
from __future__ import annotations

import voluptuous as vol
from datetime import date

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_CYCLE_START,
    CONF_CYCLE_LENGTH,
    CONF_PERIOD_LENGTH,
    DEFAULT_CYCLE_LENGTH,
    DEFAULT_PERIOD_LENGTH,
)


class CycleTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cycle Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                date.fromisoformat(user_input[CONF_CYCLE_START])
            except ValueError:
                errors[CONF_CYCLE_START] = "invalid_date"

            if not errors:
                await self.async_set_unique_id(
                    f"cycle_tracker_{user_input[CONF_NAME].lower().replace(' ', '_')}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Cycle Tracker – {user_input[CONF_NAME]}",
                    data=user_input,
                )

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="Ana"): str,
            vol.Required(CONF_CYCLE_START, default=date.today().isoformat()): str,
            vol.Optional(CONF_CYCLE_LENGTH, default=DEFAULT_CYCLE_LENGTH): vol.All(
                vol.Coerce(int), vol.Range(min=21, max=40)
            ),
            vol.Optional(CONF_PERIOD_LENGTH, default=DEFAULT_PERIOD_LENGTH): vol.All(
                vol.Coerce(int), vol.Range(min=2, max=10)
            ),
            vol.Optional("notify_device", default=""): str,
            vol.Optional("notify_period", default=True): bool,
            vol.Optional("notify_ovulation", default=True): bool,
            vol.Optional("notify_daily", default=False): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CycleTrackerOptionsFlow(config_entry)


class CycleTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._entry,
                data={**self._entry.data, **user_input},
            )
            return self.async_create_entry(title="", data=user_input)

        data = self._entry.data
        schema = vol.Schema({
            vol.Required(CONF_CYCLE_START, default=data.get(CONF_CYCLE_START, date.today().isoformat())): str,
            vol.Optional(CONF_CYCLE_LENGTH, default=data.get(CONF_CYCLE_LENGTH, DEFAULT_CYCLE_LENGTH)): vol.All(
                vol.Coerce(int), vol.Range(min=21, max=40)
            ),
            vol.Optional(CONF_PERIOD_LENGTH, default=data.get(CONF_PERIOD_LENGTH, DEFAULT_PERIOD_LENGTH)): vol.All(
                vol.Coerce(int), vol.Range(min=2, max=10)
            ),
            vol.Optional("notify_period", default=data.get("notify_period", True)): bool,
            vol.Optional("notify_ovulation", default=data.get("notify_ovulation", True)): bool,
            vol.Optional("notify_daily", default=data.get("notify_daily", False)): bool,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
