import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN



_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_TYPES = {
    "status.energyFlow.batteryStatus_charging": {
        "name": "Battery Charging",
        "device_class": BinarySensorDeviceClass.BATTERY_CHARGING,
        "entity_category": None,
    },
    "status.energyFlow.batteryStatus_discharging": {
        "name": "Battery Discharging",
        "device_class": BinarySensorDeviceClass.POWER,
        "entity_category": None,
    },
    "device.powerState": {
        "name": "Inverter Power State",
        "device_class": BinarySensorDeviceClass.POWER,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "notifications.has_unread": {
        "name": "Has Unread Notifications",
        "device_class": None,
        "entity_category": None,
    },
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    entities = [
        EatonXStorageBinarySensor(coordinator, key, description)
        for key, description in BINARY_SENSOR_TYPES.items()
    ]
    async_add_entities(entities)

class EatonXStorageBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, key, description):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._key = key
        self._name = description["name"]
        self._device_class = description["device_class"]
        self._entity_category = description["entity_category"]

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"eaton_xstorage_binary_{self._key}"

    @property
    def is_on(self):
        try:
            if self._key == "status.energyFlow.batteryStatus_charging":
                value = self.coordinator.data.get("status", {}).get("energyFlow", {}).get("batteryStatus", None)
                return value == "BAT_CHARGING"
            elif self._key == "status.energyFlow.batteryStatus_discharging":
                value = self.coordinator.data.get("status", {}).get("energyFlow", {}).get("batteryStatus", None)
                return value == "BAT_DISCHARGING"
            elif self._key == "device.powerState":
                value = self.coordinator.data.get("device", {}).get("powerState", None)
                return bool(value)
            elif self._key == "notifications.has_unread":
                unread_count = self.coordinator.data.get("unread_notifications_count", {}).get("total", 0)
                return unread_count > 0
            return False
        except Exception as e:
            _LOGGER.error(f"Error retrieving binary state for {self._key}: {e}")
            return False

    @property
    def device_class(self):
        return self._device_class

    @property
    def entity_category(self):
        return self._entity_category

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def should_poll(self):
        return False
