"""Sensor platform for the Lease Contract integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LeaseContractCoordinator

UNIT_KM = "km"
UNIT_DAYS = "d"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the five contract sensors for this config entry."""
    coordinator: LeaseContractCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            KmLeftSensor(coordinator, entry),
            MonthlyAverageLeftSensor(coordinator, entry),
            MonthlyAverageUsedSensor(coordinator, entry),
            KmLeftCurrentMonthSensor(coordinator, entry),
            DaysLeftSensor(coordinator, entry),
        ]
    )


class LeaseContractSensorBase(CoordinatorEntity[LeaseContractCoordinator], SensorEntity):
    """Common base: groups all five sensors under one device per contract."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LeaseContractCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Lease Contract",
            model="Car Lease Contract",
        )


class KmLeftSensor(LeaseContractSensorBase):
    """Km left in the whole contract."""

    _attr_name = "Km left"
    _attr_icon = "mdi:map-marker-distance"
    _attr_native_unit_of_measurement = UNIT_KM
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_km_left"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.km_left


class MonthlyAverageLeftSensor(LeaseContractSensorBase):
    """Monthly average of km left, spread over the remaining full months."""

    _attr_name = "Monthly average km left"
    _attr_icon = "mdi:calendar-range"
    _attr_native_unit_of_measurement = UNIT_KM
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_monthly_avg_km_left"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.monthly_avg_left_km

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return None
        return {"full_months_remaining": self.coordinator.data.full_months_remaining}


class MonthlyAverageUsedSensor(LeaseContractSensorBase):
    """Monthly average of km used since contract start."""

    _attr_name = "Monthly average km used"
    _attr_icon = "mdi:calendar-check"
    _attr_native_unit_of_measurement = UNIT_KM
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_monthly_avg_km_used"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.monthly_avg_used_km

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return None
        return {
            "full_months_elapsed": self.coordinator.data.full_months_elapsed,
            "used_km": self.coordinator.data.used_km,
        }


class KmLeftCurrentMonthSensor(LeaseContractSensorBase):
    """Km left within the current calendar month.

    Based on the current 'monthly average km left' entity, minus what has
    already been driven since the start of this calendar month.
    """

    _attr_name = "Km left this month"
    _attr_icon = "mdi:map-marker-distance"
    _attr_native_unit_of_measurement = UNIT_KM
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_km_left_current_month"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.km_left_current_month


class DaysLeftSensor(LeaseContractSensorBase):
    """Days left until the contract end date."""

    _attr_name = "Days left"
    _attr_icon = "mdi:calendar-clock"
    _attr_native_unit_of_measurement = UNIT_DAYS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_days_left"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.days_left
