"""Config flow for Cycle Tracker – UI wizard, zero YAML needed."""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_USER_NAME, CONF_CYCLE_START, CONF_CYCLE_LENGTH,
    CONF_PERIOD_LENGTH, CONF_NOTIFY_DEVICE, CONF_DAILY_SUMMARY,
    CONF_NOTIFY_PERIOD, CONF_NOTIFY_OVULATION,
    DEFAULT_CYCLE_LENGTH, DEFAULT_PERIOD_LENGTH,
)

_LOGGER = logging.getLogger(__name__)


def _get_notify_services(hass) -> list[str]:
    """Return list of available notify services."""
    services = hass.services.async_services().get("notify", {})
    result = [f"notify.{svc}" for svc in services if svc != "send_message"]
    return result if result else ["notify.notify"]


def _validate_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise vol.Invalid("invalid_date")
    if parsed > date.today():
        raise vol.Invalid("future_date")
    return value


class CycleTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI wizard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        notify_options = _get_notify_services(self.hass)

        if user_input is not None:
            # Validate
            try:
                _validate_date(user_input[CONF_CYCLE_START])
            except vol.Invalid as e:
                errors[CONF_CYCLE_START] = str(e)

            cl = user_input.get(CONF_CYCLE_LENGTH, DEFAULT_CYCLE_LENGTH)
            if not (21 <= cl <= 40):
                errors[CONF_CYCLE_LENGTH] = "invalid_cycle"

            if not errors:
                # Use name as unique_id so one entry per person
                user_slug = user_input[CONF_USER_NAME].lower().replace(" ", "_")
                await self.async_set_unique_id(f"cycle_tracker_{user_slug}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Cycle Tracker – {user_input[CONF_USER_NAME]}",
                    data=user_input,
                )

        # Build form schema
        today_str = date.today().isoformat()
        schema = vol.Schema({
            vol.Required(CONF_USER_NAME, default="Ana"): str,
            vol.Required(CONF_CYCLE_START, default=today_str): str,
            vol.Required(CONF_CYCLE_LENGTH, default=DEFAULT_CYCLE_LENGTH): vol.All(
                vol.Coerce(int), vol.Range(min=21, max=40)
            ),
            vol.Required(CONF_PERIOD_LENGTH, default=DEFAULT_PERIOD_LENGTH): vol.All(
                vol.Coerce(int), vol.Range(min=2, max=10)
            ),
            vol.Optional(CONF_NOTIFY_DEVICE, default=notify_options[0] if notify_options else "notify.notify"):
                vol.In(notify_options) if notify_options else str,
            vol.Optional(CONF_DAILY_SUMMARY, default=True): bool,
            vol.Optional(CONF_NOTIFY_PERIOD, default=True): bool,
            vol.Optional(CONF_NOTIFY_OVULATION, default=True): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={"today": today_str},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CycleTrackerOptionsFlow(config_entry)


class CycleTrackerOptionsFlow(config_entries.OptionsFlow):
    """Options flow – editable any time from Settings → Integrations."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        current = {**self.config_entry.data, **self.config_entry.options}
        notify_options = _get_notify_services(self.hass)

        if user_input is not None:
            try:
                _validate_date(user_input[CONF_CYCLE_START])
            except vol.Invalid as e:
                errors[CONF_CYCLE_START] = str(e)

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                CONF_CYCLE_START,
                default=current.get(CONF_CYCLE_START, date.today().isoformat()),
            ): str,
            vol.Required(
                CONF_CYCLE_LENGTH,
                default=int(current.get(CONF_CYCLE_LENGTH, DEFAULT_CYCLE_LENGTH)),
            ): vol.All(vol.Coerce(int), vol.Range(min=21, max=40)),
            vol.Required(
                CONF_PERIOD_LENGTH,
                default=int(current.get(CONF_PERIOD_LENGTH, DEFAULT_PERIOD_LENGTH)),
            ): vol.All(vol.Coerce(int), vol.Range(min=2, max=10)),
            vol.Optional(
                CONF_NOTIFY_DEVICE,
                default=current.get(CONF_NOTIFY_DEVICE, notify_options[0] if notify_options else "notify.notify"),
            ): vol.In(notify_options) if notify_options else str,
            vol.Optional(
                CONF_DAILY_SUMMARY,
                default=bool(current.get(CONF_DAILY_SUMMARY, True)),
            ): bool,
            vol.Optional(
                CONF_NOTIFY_PERIOD,
                default=bool(current.get(CONF_NOTIFY_PERIOD, True)),
            ): bool,
            vol.Optional(
                CONF_NOTIFY_OVULATION,
                default=bool(current.get(CONF_NOTIFY_OVULATION, True)),
            ): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
