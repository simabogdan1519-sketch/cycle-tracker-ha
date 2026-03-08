"""Cycle Tracker – Senzori v2.0"""
from __future__ import annotations
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    prefix = entry.data.get("name", "user").lower().replace(" ", "_")
    sensors = [
        CycleTrackerSensor(hass, entry, prefix, "cycle_day",          "Cycle Day",         "mdi:counter",          None),
        CycleTrackerSensor(hass, entry, prefix, "cycle_phase",        "Cycle Phase",        "mdi:flower",           None),
        CycleTrackerSensor(hass, entry, prefix, "fertility_level",    "Fertility Level",    "mdi:egg",              None),
        CycleTrackerSensor(hass, entry, prefix, "days_until_period",  "Days Until Period",  "mdi:calendar-clock",   "d"),
        CycleTrackerSensor(hass, entry, prefix, "next_period_date",   "Next Period Date",   "mdi:calendar-today",   None),
        CycleTrackerSensor(hass, entry, prefix, "ovulation_date",     "Ovulation Date",     "mdi:calendar-star",    None),
        CycleTrackerSensor(hass, entry, prefix, "cycle_progress",     "Cycle Progress",     "mdi:progress-clock",   "%"),
        CycleTrackerSensor(hass, entry, prefix, "cycle_history",      "Cycle History",      "mdi:history",          None),
    ]
    async_add_entities(sensors, True)


class CycleTrackerSensor(SensorEntity):
    def __init__(self, hass, entry, prefix, sensor_key, friendly_name, icon, unit):
        self._hass = hass
        self._entry = entry
        self._entry_id = entry.entry_id
        self._prefix = prefix
        self._sensor_key = sensor_key
        self._attr_name = f"{prefix.capitalize()} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    @property
    def entity_id(self):
        return f"sensor.{self._prefix}_{self._sensor_key}"

    async def async_update(self) -> None:
        data = self._hass.data.get(DOMAIN, {}).get(self._entry_id, {})
        if not data:
            return

        if self._sensor_key == "cycle_history":
            history = data.get("cycle_history", [])
            self._attr_native_value = len(history)
            self._attr_extra_state_attributes = {
                "history": json.dumps(history),
                "avg_cycle_length": data.get("avg_cycle_length", 28),
                "avg_period_length": data.get("avg_period_length", 5),
                "is_irregular": data.get("is_irregular", False),
                "trend": data.get("trend", "stable"),
                "history_count": data.get("history_count", 0),
            }

        elif self._sensor_key == "cycle_day":
            self._attr_native_value = data.get("cycle_day")
            self._attr_extra_state_attributes = {
                "cycle_length":  data.get("cycle_length", 28),
                "period_length": data.get("period_length", 5),
                "ovulation_day": data.get("ovulation_day", 14),
            }

        elif self._sensor_key == "cycle_phase":
            self._attr_native_value = data.get("cycle_phase")

        elif self._sensor_key == "fertility_level":
            self._attr_native_value = data.get("fertility_level")

        elif self._sensor_key == "days_until_period":
            self._attr_native_value = data.get("days_until_period")

        elif self._sensor_key == "next_period_date":
            self._attr_native_value = data.get("next_period_date")

        elif self._sensor_key == "ovulation_date":
            self._attr_native_value = data.get("ovulation_date")

        elif self._sensor_key == "cycle_progress":
            self._attr_native_value = data.get("cycle_progress")
