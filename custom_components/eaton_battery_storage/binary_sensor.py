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
        "device_class": BinarySensorDeviceClass.BATTERY,
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
            value = self.coordinator.data.get("status", {}).get("energyFlow", {}).get("batteryStatus", None)
            if self._key == "status.energyFlow.batteryStatus_charging":
                return value == "BAT_CHARGING"
            elif self._key == "status.energyFlow.batteryStatus_discharging":
                return value == "BAT_DISCHARGING"
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
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.host)},
            "name": "Eaton xStorage Home",
            "manufacturer": "Eaton",
            "model": "xStorage Home",
            "entry_type": "service",
            "configuration_url": f"https://{self.coordinator.api.host}",
        }

    @property
    def should_poll(self):
        return False
