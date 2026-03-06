"""Cycle Tracker – Home Assistant Custom Integration."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN, CONF_CYCLE_START, CONF_CYCLE_LENGTH, CONF_PERIOD_LENGTH,
    CONF_USER_NAME, CONF_NOTIFY_DEVICE, CONF_DAILY_SUMMARY,
    CONF_NOTIFY_PERIOD, CONF_NOTIFY_OVULATION,
    DEFAULT_CYCLE_LENGTH, DEFAULT_PERIOD_LENGTH,
    PHASE_MENSTRUATION, PHASE_FOLLICULAR, PHASE_OVULATION, PHASE_LUTEAL,
    PHASE_LABELS, PHASE_ICONS,
    FERTILITY_MAXIMUM, FERTILITY_VERY_HIGH, FERTILITY_HIGH,
    FERTILITY_MODERATE, FERTILITY_LOW, FERTILITY_LABELS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

UPDATE_INTERVAL = timedelta(minutes=30)


# ─── Service schema ────────────────────────────────────────────────────────────
SERVICE_UPDATE_CYCLE = "update_cycle"
SERVICE_SCHEMA_UPDATE = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("cycle_start_date"): cv.string,
    vol.Optional("cycle_length", default=DEFAULT_CYCLE_LENGTH): vol.All(int, vol.Range(min=21, max=40)),
    vol.Optional("period_length", default=DEFAULT_PERIOD_LENGTH): vol.All(int, vol.Range(min=2, max=10)),
})


# ─── Core calculation helpers ──────────────────────────────────────────────────
def calculate_cycle_data(
    start_date_str: str,
    cycle_length: int,
    period_length: int,
) -> dict:
    """Calculate all cycle metrics from a start date string (YYYY-MM-DD)."""
    today = date.today()

    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        return _empty_cycle_data()

    diff = (today - start).days
    if diff < 0:
        return _empty_cycle_data()

    day_of_cycle = (diff % cycle_length) + 1
    ovulation_day = round(cycle_length / 2)
    days_until_period = cycle_length - day_of_cycle
    progress_pct = round((day_of_cycle / cycle_length) * 100)

    # Phase
    if day_of_cycle <= period_length:
        phase = PHASE_MENSTRUATION
    elif day_of_cycle <= ovulation_day - 3:
        phase = PHASE_FOLLICULAR
    elif day_of_cycle <= ovulation_day + 1:
        phase = PHASE_OVULATION
    else:
        phase = PHASE_LUTEAL

    # Fertility
    dist = abs(day_of_cycle - ovulation_day)
    if dist <= 1:
        fertility = FERTILITY_MAXIMUM
    elif dist <= 2:
        fertility = FERTILITY_VERY_HIGH
    elif dist <= 3:
        fertility = FERTILITY_HIGH
    elif dist <= 5:
        fertility = FERTILITY_MODERATE
    else:
        fertility = FERTILITY_LOW

    # Next period date
    cycles_elapsed = diff // cycle_length
    next_period = start + timedelta(days=(cycles_elapsed + 1) * cycle_length)

    # Ovulation date (this cycle)
    cycle_start_this = start + timedelta(days=cycles_elapsed * cycle_length)
    ovulation_date = cycle_start_this + timedelta(days=ovulation_day - 1)

    return {
        "day_of_cycle":       day_of_cycle,
        "cycle_length":       cycle_length,
        "period_length":      period_length,
        "ovulation_day":      ovulation_day,
        "phase":              phase,
        "phase_label":        PHASE_LABELS[phase],
        "phase_icon":         PHASE_ICONS[phase],
        "fertility":          fertility,
        "fertility_label":    FERTILITY_LABELS[fertility],
        "days_until_period":  days_until_period,
        "progress_pct":       progress_pct,
        "next_period_date":   next_period.isoformat(),
        "ovulation_date":     ovulation_date.isoformat(),
        "cycle_start_date":   start_date_str,
    }


def _empty_cycle_data() -> dict:
    return {
        "day_of_cycle": 1, "cycle_length": DEFAULT_CYCLE_LENGTH,
        "period_length": DEFAULT_PERIOD_LENGTH, "ovulation_day": 14,
        "phase": PHASE_FOLLICULAR, "phase_label": "Foliculară",
        "phase_icon": "mdi:flower-outline", "fertility": FERTILITY_LOW,
        "fertility_label": "Scăzut", "days_until_period": DEFAULT_CYCLE_LENGTH - 1,
        "progress_pct": 0, "next_period_date": None, "ovulation_date": None,
        "cycle_start_date": None,
    }


# ─── Coordinator ───────────────────────────────────────────────────────────────
class CycleTrackerCoordinator(DataUpdateCoordinator):
    """Manages data refresh and holds current cycle state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry

    async def _async_update_data(self) -> dict:
        opts = {**self.entry.data, **self.entry.options}
        return calculate_cycle_data(
            opts.get(CONF_CYCLE_START, ""),
            int(opts.get(CONF_CYCLE_LENGTH, DEFAULT_CYCLE_LENGTH)),
            int(opts.get(CONF_PERIOD_LENGTH, DEFAULT_PERIOD_LENGTH)),
        )


# ─── Setup ─────────────────────────────────────────────────────────────────────
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cycle Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = CycleTrackerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener (options flow)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    # Register services
    _register_services(hass)

    # Schedule daily notifications
    _schedule_notifications(hass, entry, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator: CycleTrackerCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_request_refresh()


def _register_services(hass: HomeAssistant) -> None:
    """Register integration services (callable from automations/scripts)."""

    async def handle_update_cycle(call: ServiceCall) -> None:
        entry_id   = call.data["entry_id"]
        start_date = call.data["cycle_start_date"]
        cycle_len  = call.data.get("cycle_length", DEFAULT_CYCLE_LENGTH)
        period_len = call.data.get("period_length", DEFAULT_PERIOD_LENGTH)

        if entry_id not in hass.data.get(DOMAIN, {}):
            _LOGGER.error("cycle_tracker: entry_id '%s' not found", entry_id)
            return

        coordinator: CycleTrackerCoordinator = hass.data[DOMAIN][entry_id]
        new_options = {
            **coordinator.entry.options,
            CONF_CYCLE_START:   start_date,
            CONF_CYCLE_LENGTH:  cycle_len,
            CONF_PERIOD_LENGTH: period_len,
        }
        hass.config_entries.async_update_entry(coordinator.entry, options=new_options)
        await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_CYCLE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_CYCLE,
            handle_update_cycle,
            schema=SERVICE_SCHEMA_UPDATE,
        )


def _schedule_notifications(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: CycleTrackerCoordinator,
) -> None:
    """Set up time-based notification triggers via HA event listener."""
    import homeassistant.util.dt as dt_util
    from homeassistant.helpers.event import async_track_time_change

    opts = {**entry.data, **entry.options}
    notify_svc   = opts.get(CONF_NOTIFY_DEVICE, "notify.notify")
    daily        = opts.get(CONF_DAILY_SUMMARY, True)
    notify_period = opts.get(CONF_NOTIFY_PERIOD, True)
    notify_ovul  = opts.get(CONF_NOTIFY_OVULATION, True)
    user_name    = opts.get(CONF_USER_NAME, "")

    async def _send_daily(now) -> None:  # noqa: ANN001
        data = coordinator.data
        if not data:
            return
        phase_label = data.get("phase_label", "")
        day         = data.get("day_of_cycle", "?")
        left        = data.get("days_until_period", "?")

        # Period soon
        if notify_period and left == 3:
            next_p = data.get("next_period_date", "")
            await hass.services.async_call(
                "notify", notify_svc.replace("notify.", "", 1),
                {"title": "🌸 Cycle Tracker",
                 "message": f"Menstruația estimată în 3 zile ({next_p}). Pregătește-te! 💊🛁",
                 "data": {"tag": f"cycle_period_soon_{entry.entry_id}"}},
                blocking=False,
            )

        # Ovulation
        if notify_ovul and data.get("fertility") == FERTILITY_MAXIMUM:
            await hass.services.async_call(
                "notify", notify_svc.replace("notify.", "", 1),
                {"title": "✨ Cycle Tracker – Ovulație",
                 "message": "Fertilitate maximă azi! Energie la cote înalte. ✨",
                 "data": {"tag": f"cycle_ovulation_{entry.entry_id}"}},
                blocking=False,
            )

        # Daily summary
        if daily:
            await hass.services.async_call(
                "notify", notify_svc.replace("notify.", "", 1),
                {"title": f"🌸 Bună dimineața{', ' + user_name if user_name else ''}!",
                 "message": f"Ziua {day} din ciclu – {phase_label}. {left} zile rămase.",
                 "data": {"tag": f"cycle_daily_{entry.entry_id}"}},
                blocking=False,
            )

    async_track_time_change(hass, _send_daily, hour=8, minute=0, second=0)
