"""Cycle Tracker – Home Assistant Custom Integration v2.0
Suport complet pentru istoric cicluri (date, durată menstruație, flux).
Surse medicale: Wilcox et al. BMJ 2000, Johns Hopkins, ACOG.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import async_get_platforms

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

SERVICE_UPDATE_CYCLE  = "update_cycle"
SERVICE_ADD_PAST_CYCLE = "add_past_cycle"
SERVICE_DELETE_CYCLE  = "delete_cycle"

SCHEMA_UPDATE_CYCLE = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("cycle_start_date"): cv.string,
    vol.Optional("period_length", default=5): vol.Coerce(int),
    vol.Optional("flow_intensity", default="mediu"): cv.string,
})

SCHEMA_ADD_PAST_CYCLE = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("date"): cv.string,
    vol.Optional("period_length", default=5): vol.Coerce(int),
    vol.Optional("flow_intensity", default="mediu"): cv.string,
})

SCHEMA_DELETE_CYCLE = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("date"): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Migrare v1 → v2: dacă nu există cycle_history, creează din date vechi
    data = dict(entry.data)
    if "cycle_history" not in data:
        history = []
        if "cycle_start_date" in data:
            history.append({
                "date": data["cycle_start_date"],
                "period_length": data.get("period_length", 5),
                "flow_intensity": "mediu",
                "source": "migrated",
            })
        data["cycle_history"] = history
        hass.config_entries.async_update_entry(entry, data=data)

    hass.data[DOMAIN][entry.entry_id] = _calculate(entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_UPDATE_CYCLE):
        return

    async def handle_update_cycle(call: ServiceCall) -> None:
        entry = hass.config_entries.async_get_entry(call.data["entry_id"])
        if not entry:
            return
        history = list(entry.data.get("cycle_history", []))
        new_date = call.data["cycle_start_date"]
        new_entry = {
            "date": new_date,
            "period_length": call.data.get("period_length", 5),
            "flow_intensity": call.data.get("flow_intensity", "mediu"),
            "source": "current",
        }
        idx = next((i for i, x in enumerate(history) if x["date"] == new_date), None)
        if idx is not None:
            history[idx] = new_entry
        else:
            history.append(new_entry)

        new_data = {
            **entry.data,
            "cycle_start_date": new_date,
            "cycle_length": _smart_cycle_length(history),
            "period_length": call.data.get("period_length", 5),
            "cycle_history": history,
        }
        hass.config_entries.async_update_entry(entry, data=new_data)
        hass.data[DOMAIN][entry.entry_id] = _calculate(new_data)
        await _refresh_sensors(hass, entry.entry_id)

    async def handle_add_past_cycle(call: ServiceCall) -> None:
        entry = hass.config_entries.async_get_entry(call.data["entry_id"])
        if not entry:
            return
        history = list(entry.data.get("cycle_history", []))
        new_date = call.data["date"]
        if any(x["date"] == new_date for x in history):
            _LOGGER.warning("Cycle Tracker: data %s există deja în istoric", new_date)
            return
        history.append({
            "date": new_date,
            "period_length": call.data.get("period_length", 5),
            "flow_intensity": call.data.get("flow_intensity", "mediu"),
            "source": "past",
        })
        new_data = {
            **entry.data,
            "cycle_length": _smart_cycle_length(history),
            "cycle_history": history,
        }
        hass.config_entries.async_update_entry(entry, data=new_data)
        hass.data[DOMAIN][entry.entry_id] = _calculate(new_data)
        await _refresh_sensors(hass, entry.entry_id)

    async def handle_delete_cycle(call: ServiceCall) -> None:
        entry = hass.config_entries.async_get_entry(call.data["entry_id"])
        if not entry:
            return
        history = [x for x in entry.data.get("cycle_history", []) if x["date"] != call.data["date"]]
        new_data = {
            **entry.data,
            "cycle_length": _smart_cycle_length(history) if len(history) >= 2 else entry.data.get("cycle_length", 28),
            "cycle_history": history,
        }
        hass.config_entries.async_update_entry(entry, data=new_data)
        hass.data[DOMAIN][entry.entry_id] = _calculate(new_data)
        await _refresh_sensors(hass, entry.entry_id)

    hass.services.async_register(DOMAIN, SERVICE_UPDATE_CYCLE,   handle_update_cycle,   schema=SCHEMA_UPDATE_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_ADD_PAST_CYCLE, handle_add_past_cycle, schema=SCHEMA_ADD_PAST_CYCLE)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_CYCLE,   handle_delete_cycle,   schema=SCHEMA_DELETE_CYCLE)


async def _refresh_sensors(hass: HomeAssistant, entry_id: str) -> None:
    for platform in async_get_platforms(hass, DOMAIN):
        for entity in platform.entities.values():
            if hasattr(entity, "_entry_id") and entity._entry_id == entry_id:
                entity.async_schedule_update_ha_state(True)


# ── Logică medicală ────────────────────────────────────────────────────────

def _smart_cycle_length(history: list) -> int:
    """Durata medie din istoric. Default 28 dacă date insuficiente."""
    if len(history) < 2:
        return 28
    sorted_h = sorted(history, key=lambda x: x["date"])
    lengths = []
    for i in range(1, len(sorted_h)):
        try:
            d1 = datetime.strptime(sorted_h[i-1]["date"], "%Y-%m-%d").date()
            d2 = datetime.strptime(sorted_h[i]["date"], "%Y-%m-%d").date()
            diff = (d2 - d1).days
            if 15 <= diff <= 50:
                lengths.append(diff)
        except ValueError:
            continue
    return round(sum(lengths) / len(lengths)) if lengths else 28


def _calculate(data: dict) -> dict:
    today = date.today()
    history = data.get("cycle_history", [])

    # Cycle length din istoric sau config
    cycle_length = _smart_cycle_length(history) if len(history) >= 2 else data.get("cycle_length", 28)

    # Cel mai recent ciclu = point de start
    if history:
        sorted_h = sorted(history, key=lambda x: x["date"], reverse=True)
        latest = sorted_h[0]
        try:
            cycle_start = datetime.strptime(latest["date"], "%Y-%m-%d").date()
        except ValueError:
            cycle_start = today
        period_length = latest.get("period_length", data.get("period_length", 5))
    else:
        try:
            cycle_start = datetime.strptime(data.get("cycle_start_date", str(today)), "%Y-%m-%d").date()
        except ValueError:
            cycle_start = today
        period_length = data.get("period_length", 5)

    ovulation_day = cycle_length - 14

    days_elapsed = max((today - cycle_start).days, 0)
    cycle_day = (days_elapsed % cycle_length) + 1

    # Faza (Johns Hopkins / ACOG)
    if cycle_day <= period_length:
        phase = "menstruatie"
    elif cycle_day < ovulation_day - 1:
        phase = "foliculara"
    elif cycle_day in (ovulation_day - 1, ovulation_day):
        phase = "ovulatie"
    else:
        phase = "luteala"

    # Fertilitate (Wilcox N Engl J Med 1995)
    rel = cycle_day - ovulation_day
    if rel in (-1, 0):
        fertility = "maxim"
    elif rel == -2:
        fertility = "foarte_inalt"
    elif -5 <= rel <= -3:
        fertility = "inalt"
    elif rel == 1:
        fertility = "moderat"
    else:
        fertility = "scazut"

    days_until_period = cycle_length - (days_elapsed % cycle_length)
    if days_until_period == cycle_length:
        days_until_period = 0
    next_period = today + timedelta(days=days_until_period)

    cycles_passed = days_elapsed // cycle_length
    ovulation_date = cycle_start + timedelta(days=cycles_passed * cycle_length + ovulation_day - 1)
    if ovulation_date < today:
        ovulation_date = cycle_start + timedelta(days=(cycles_passed + 1) * cycle_length + ovulation_day - 1)

    progress = round((cycle_day / cycle_length) * 100)

    # Statistici istoric
    stats = _calc_history_stats(history)

    return {
        "cycle_day": cycle_day,
        "cycle_phase": phase,
        "fertility_level": fertility,
        "days_until_period": days_until_period,
        "next_period_date": str(next_period),
        "ovulation_date": str(ovulation_date),
        "cycle_progress": progress,
        "cycle_length": cycle_length,
        "period_length": period_length,
        "ovulation_day": ovulation_day,
        "cycle_history": history,
        **stats,
    }


def _calc_history_stats(history: list) -> dict:
    if len(history) < 2:
        return {
            "history_count": len(history),
            "avg_cycle_length": 28,
            "avg_period_length": 5,
            "is_irregular": False,
            "trend": "insufficient_data",
        }
    sorted_h = sorted(history, key=lambda x: x["date"])
    lengths = []
    for i in range(1, len(sorted_h)):
        try:
            d1 = datetime.strptime(sorted_h[i-1]["date"], "%Y-%m-%d").date()
            d2 = datetime.strptime(sorted_h[i]["date"], "%Y-%m-%d").date()
            diff = (d2 - d1).days
            if 15 <= diff <= 50:
                lengths.append(diff)
        except ValueError:
            continue

    avg_len = round(sum(lengths) / len(lengths)) if lengths else 28

    is_irregular = False
    if len(lengths) >= 2:
        mean = sum(lengths) / len(lengths)
        std = (sum((x - mean) ** 2 for x in lengths) / len(lengths)) ** 0.5
        is_irregular = std > 4

    trend = "stable"
    if len(lengths) >= 4:
        half = len(lengths) // 2
        a1 = sum(lengths[:half]) / half
        a2 = sum(lengths[-half:]) / half
        if a2 - a1 > 2:
            trend = "longer"
        elif a1 - a2 > 2:
            trend = "shorter"

    p_lens = [x.get("period_length", 5) for x in history if x.get("period_length")]
    avg_period = round(sum(p_lens) / len(p_lens)) if p_lens else 5

    return {
        "history_count": len(history),
        "avg_cycle_length": avg_len,
        "avg_period_length": avg_period,
        "is_irregular": is_irregular,
        "trend": trend,
    }
