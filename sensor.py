"""Sensor platform for Cycle Tracker – 7 sensors created automatically."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CONF_USER_NAME,
    SENSOR_CYCLE_DAY, SENSOR_CYCLE_PHASE, SENSOR_FERTILITY_LEVEL,
    SENSOR_DAYS_UNTIL_PERIOD, SENSOR_NEXT_PERIOD_DATE,
    SENSOR_OVULATION_DATE, SENSOR_CYCLE_PROGRESS,
    PHASE_LABELS, PHASE_ICONS, FERTILITY_LABELS,
)
from . import CycleTrackerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CycleTrackerCoordinator = hass.data[DOMAIN][entry.entry_id]
    user_name = entry.data.get(CONF_USER_NAME, "User")

    async_add_entities([
        CycleDaySensor(coordinator, entry, user_name),
        CyclePhaseSensor(coordinator, entry, user_name),
        FertilityLevelSensor(coordinator, entry, user_name),
        DaysUntilPeriodSensor(coordinator, entry, user_name),
        NextPeriodDateSensor(coordinator, entry, user_name),
        OvulationDateSensor(coordinator, entry, user_name),
        CycleProgressSensor(coordinator, entry, user_name),
    ], update_before_add=True)


def _device_info(entry: ConfigEntry, user_name: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"Cycle Tracker – {user_name}",
        manufacturer="Cycle Tracker",
        model="Menstrual Cycle Monitor",
        sw_version="1.0.0",
        entry_type="service",
    )


class _CycleBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for all Cycle Tracker sensors."""

    def __init__(
        self,
        coordinator: CycleTrackerCoordinator,
        entry: ConfigEntry,
        user_name: str,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry     = entry
        self._user_name = user_name
        self._key       = key
        self._attr_name = f"{user_name} – {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = _device_info(entry, user_name)

    @property
    def _data(self) -> dict:
        return self.coordinator.data or {}


# ─── Individual sensors ────────────────────────────────────────────────────────

class CycleDaySensor(_CycleBaseSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ziua"

    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_CYCLE_DAY, "Ziua ciclului", "mdi:counter")

    @property
    def native_value(self):
        return self._data.get("day_of_cycle")

    @property
    def extra_state_attributes(self):
        return {
            "cycle_length":  self._data.get("cycle_length"),
            "period_length": self._data.get("period_length"),
            "ovulation_day": self._data.get("ovulation_day"),
        }


class CyclePhaseSensor(_CycleBaseSensor):
    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_CYCLE_PHASE, "Faza ciclului", "mdi:flower")

    @property
    def native_value(self):
        return self._data.get("phase")

    @property
    def icon(self):
        return self._data.get("phase_icon", "mdi:flower")

    @property
    def extra_state_attributes(self):
        return {
            "phase_label": self._data.get("phase_label"),
            "description": _phase_description(self._data.get("phase", "")),
        }


class FertilityLevelSensor(_CycleBaseSensor):
    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_FERTILITY_LEVEL, "Nivel fertilitate", "mdi:leaf")

    @property
    def native_value(self):
        return self._data.get("fertility")

    @property
    def extra_state_attributes(self):
        return {"fertility_label": self._data.get("fertility_label")}


class DaysUntilPeriodSensor(_CycleBaseSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "zile"

    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_DAYS_UNTIL_PERIOD, "Zile până la menstruație", "mdi:calendar-clock")

    @property
    def native_value(self):
        return self._data.get("days_until_period")


class NextPeriodDateSensor(_CycleBaseSensor):
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_NEXT_PERIOD_DATE, "Următoarea menstruație", "mdi:calendar-alert")

    @property
    def native_value(self):
        val = self._data.get("next_period_date")
        if val:
            from datetime import date as d
            try:
                return d.fromisoformat(val)
            except ValueError:
                return None
        return None


class OvulationDateSensor(_CycleBaseSensor):
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_OVULATION_DATE, "Data ovulației", "mdi:egg-outline")

    @property
    def native_value(self):
        val = self._data.get("ovulation_date")
        if val:
            from datetime import date as d
            try:
                return d.fromisoformat(val)
            except ValueError:
                return None
        return None


class CycleProgressSensor(_CycleBaseSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coord, entry, user):
        super().__init__(coord, entry, user, SENSOR_CYCLE_PROGRESS, "Progres ciclu", "mdi:progress-clock")

    @property
    def native_value(self):
        return self._data.get("progress_pct")


# ─── Phase descriptions ────────────────────────────────────────────────────────
def _phase_description(phase: str) -> str:
    return {
        "menstruatie": "Corpul se regenerează. Odihnă, căldură și hidratare.",
        "foliculara":  "Energia revine. Ideal pentru activitate fizică și planuri noi.",
        "ovulatie":    "Vârf de fertilitate. Energie și comunicare la cote maxime.",
        "luteala":     "Pregătire pentru un nou ciclu. Introspecție și confort.",
    }.get(phase, "")
