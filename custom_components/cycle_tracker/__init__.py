"""Cycle Tracker – Home Assistant Integration."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_CYCLE_START,
    CONF_CYCLE_LENGTH,
    CONF_PERIOD_LENGTH,
    DEFAULT_CYCLE_LENGTH,
    DEFAULT_PERIOD_LENGTH,
    PHASE_MENSTRUATIE,
    PHASE_FOLICULARA,
    PHASE_OVULATIE,
    PHASE_LUTEALA,
    FERTILITY_SCAZUT,
    FERTILITY_MODERAT,
    FERTILITY_INALT,
    FERTILITY_FOARTE_INALT,
    FERTILITY_MAXIM,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

UPDATE_CYCLE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("cycle_start_date"): cv.string,
    vol.Optional("cycle_length", default=DEFAULT_CYCLE_LENGTH): vol.Coerce(int),
    vol.Optional("period_length", default=DEFAULT_PERIOD_LENGTH): vol.Coerce(int),
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cycle Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = CycleTrackerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, "update_cycle"):
        async def handle_update_cycle(call: ServiceCall) -> None:
            entry_id   = call.data["entry_id"]
            start_date = call.data["cycle_start_date"]
            c_len      = call.data.get("cycle_length", DEFAULT_CYCLE_LENGTH)
            p_len      = call.data.get("period_length", DEFAULT_PERIOD_LENGTH)

            coord = hass.data[DOMAIN].get(entry_id)
            if not coord:
                _LOGGER.error("CycleTracker: entry_id '%s' nu a fost găsit", entry_id)
                return

            hass.config_entries.async_update_entry(
                coord.entry,
                data={
                    **coord.entry.data,
                    CONF_CYCLE_START:  start_date,
                    CONF_CYCLE_LENGTH: c_len,
                    CONF_PERIOD_LENGTH: p_len,
                },
            )
            await coord.async_request_refresh()

        hass.services.async_register(
            DOMAIN, "update_cycle", handle_update_cycle, schema=UPDATE_CYCLE_SCHEMA
        )

    _schedule_notifications(hass, entry, coordinator)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _schedule_notifications(hass, entry, coordinator):
    from homeassistant.helpers.event import async_track_time_change

    notify_device = entry.data.get("notify_device", "")
    notify_period = entry.data.get("notify_period", True)
    notify_ovul   = entry.data.get("notify_ovulation", True)
    notify_daily  = entry.data.get("notify_daily", False)

    if not notify_device:
        return

    async def daily_check(now):
        data = coordinator.data
        if not data:
            return
        days_left = data.get("days_until_period", 99)
        phase     = data.get("phase", "")

        if notify_period and days_left == 3:
            await hass.services.async_call("notify", notify_device, {
                "title": "🌸 Cycle Tracker",
                "message": "Pregătește-te! Menstruația vine în 3 zile.",
            })
        if notify_ovul and phase == PHASE_OVULATIE:
            await hass.services.async_call("notify", notify_device, {
                "title": "✨ Cycle Tracker",
                "message": "Fertilitate maximă azi!",
            })
        if notify_daily:
            phase_ro = {
                PHASE_MENSTRUATIE: "Menstruație",
                PHASE_FOLICULARA:  "Foliculară",
                PHASE_OVULATIE:    "Ovulație",
                PHASE_LUTEALA:     "Luteală",
            }.get(phase, phase)
            await hass.services.async_call("notify", notify_device, {
                "title": "🌸 Cycle Tracker – Bună dimineața!",
                "message": f"Faza: {phase_ro} · {days_left} zile până la menstruație.",
            })

    async_track_time_change(hass, daily_check, hour=8, minute=0, second=0)


class CycleTrackerCoordinator(DataUpdateCoordinator):
    """Calculates all cycle data and stores it."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        return self._calculate(self.entry.data)

    def _calculate(self, data: dict) -> dict:
        today = date.today()

        start_str  = data.get(CONF_CYCLE_START, "")
        cycle_len  = int(data.get(CONF_CYCLE_LENGTH, DEFAULT_CYCLE_LENGTH))
        period_len = int(data.get(CONF_PERIOD_LENGTH, DEFAULT_PERIOD_LENGTH))

        if not start_str:
            return {}

        try:
            start = date.fromisoformat(start_str)
        except ValueError:
            return {}

        while (today - start).days >= cycle_len:
            start += timedelta(days=cycle_len)

        cycle_day      = (today - start).days + 1
        ovulation_day  = cycle_len - 14
        days_until     = cycle_len - cycle_day
        next_period    = start + timedelta(days=cycle_len)
        ovulation_date = start + timedelta(days=ovulation_day - 1)
        progress       = round((cycle_day / cycle_len) * 100)

        if cycle_day <= period_len:
            phase = PHASE_MENSTRUATIE
        elif cycle_day < ovulation_day - 3:
            phase = PHASE_FOLICULARA
        elif cycle_day <= ovulation_day + 2:
            phase = PHASE_OVULATIE
        else:
            phase = PHASE_LUTEALA

        diff_ov = abs(cycle_day - ovulation_day)
        if diff_ov == 0:
            fertility = FERTILITY_MAXIM
        elif diff_ov == 1:
            fertility = FERTILITY_FOARTE_INALT
        elif diff_ov <= 3:
            fertility = FERTILITY_INALT
        elif diff_ov <= 5:
            fertility = FERTILITY_MODERAT
        else:
            fertility = FERTILITY_SCAZUT

        return {
            "cycle_day":         cycle_day,
            "phase":             phase,
            "fertility":         fertility,
            "days_until_period": days_until,
            "next_period_date":  next_period.isoformat(),
            "ovulation_date":    ovulation_date.isoformat(),
            "cycle_progress":    progress,
            "cycle_length":      cycle_len,
            "period_length":     period_len,
            "ovulation_day":     ovulation_day,
        }
