"""Cycle Tracker – Config Flow v2.0"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class CycleTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "cycle_start_date": user_input["cycle_start_date"],
                    "cycle_length": user_input.get("cycle_length", 28),
                    "period_length": user_input.get("period_length", 5),
                    "cycle_history": [{
                        "date": user_input["cycle_start_date"],
                        "period_length": user_input.get("period_length", 5),
                        "flow_intensity": "mediu",
                        "source": "initial",
                    }],
                },
            )

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("cycle_start_date"): str,
            vol.Optional("cycle_length", default=28): vol.Coerce(int),
            vol.Optional("period_length", default=5): vol.Coerce(int),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CycleTrackerOptionsFlow(config_entry)


class CycleTrackerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Optional("cycle_length", default=self._config_entry.data.get("cycle_length", 28)): vol.Coerce(int),
            vol.Optional("period_length", default=self._config_entry.data.get("period_length", 5)): vol.Coerce(int),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
