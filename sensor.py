"""Cycle Tracker – Sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_NAME


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "user").lower().replace(" ", "_")

    async_add_entities([
        CycleDaySensor(coordinator, entry, name),
        CyclePhaseSensor(coordinator, entry, name),
        FertilitySensor(coordinator, entry, name),
        DaysUntilPeriodSensor(coordinator, entry, name),
        NextPeriodSensor(coordinator, entry, name),
        OvulationSensor(coordinator, entry, name),
        CycleProgressSensor(coordinator, entry, name),
    ])


class CycleBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name_prefix, sensor_key, sensor_name, icon, unit=None):
        super().__init__(coordinator)
        self._entry       = entry
        self._prefix      = name_prefix
        self._sensor_key  = sensor_key
        self._attr_name   = f"{name_prefix.capitalize()} {sensor_name}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_icon   = icon
        if unit:
            self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._sensor_key)

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data or {}
        return {
            "entry_id":      self._entry.entry_id,
            "cycle_length":  d.get("cycle_length"),
            "period_length": d.get("period_length"),
            "ovulation_day": d.get("ovulation_day"),
        }

    @property
    def entity_id(self):
        return f"sensor.{self._prefix}{self._sensor_key}"

    @entity_id.setter
    def entity_id(self, value):
        pass


class CycleDaySensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "cycle_day", "Cycle Day", "mdi:calendar-heart", "zile")


class CyclePhaseSensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "phase", "Cycle Phase", "mdi:flower")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("phase")


class FertilitySensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "fertility", "Fertility Level", "mdi:egg")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("fertility")


class DaysUntilPeriodSensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "days_until_period", "Days Until Period", "mdi:calendar-clock", "zile")


class NextPeriodSensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "next_period_date", "Next Period Date", "mdi:calendar-month")


class OvulationSensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "ovulation_date", "Ovulation Date", "mdi:star-circle")


class CycleProgressSensor(CycleBaseSensor):
    def __init__(self, coord, entry, prefix):
        super().__init__(coord, entry, prefix, "cycle_progress", "Cycle Progress", "mdi:progress-clock", "%")
