
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .number_constants import NUMBER_ENTITIES

from homeassistant.components.sensor import SensorEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN]["coordinator"]
    # Initialize storage for number values if not present
    hass.data[DOMAIN].setdefault("number_values", {})
    number_entities = [
        EatonBatteryNumberEntity(hass, coordinator, desc)
        for desc in NUMBER_ENTITIES
    ]
    # Add wattage sensors for charge/discharge power
    wattage_sensors = [
        PowerWattageSensor(hass, desc["key"]) for desc in NUMBER_ENTITIES if desc["key"] in ("charge_power", "discharge_power")
    ]
    async_add_entities(number_entities + wattage_sensors)
class PowerWattageSensor(SensorEntity):
    def __init__(self, hass, key):
        self.hass = hass
        self._key = key
        self._attr_unique_id = f"eaton_battery_{key}_wattage"
        self._attr_name = f"{'Charge' if key == 'charge_power' else 'Discharge'} Power (Wattage)"
        self._attr_unit_of_measurement = "W"
        self._attr_icon = "mdi:flash"

    @property
    def state(self):
        percent = self.hass.data[DOMAIN]["number_values"].get(self._key)
        if percent is not None:
            try:
                return int(round((percent / 100) * 3600))
            except Exception:
                return None
        return None

    @property
    def device_info(self):
        coordinator = self.hass.data[DOMAIN]["coordinator"]
        return {
            "identifiers": {(DOMAIN, coordinator.api.host)},
            "name": "Eaton xStorage Home",
            "manufacturer": "Eaton",
            "model": "xStorage Home",
            "entry_type": "service",
            "configuration_url": f"https://{coordinator.api.host}",
        }

class EatonBatteryNumberEntity(CoordinatorEntity, NumberEntity):
    @property
    def mode(self):
        return "box"
    def __init__(self, hass, coordinator, description):
        super().__init__(coordinator)
        self.hass = hass
        self.coordinator = coordinator
        self._key = description["key"]
        self._attr_unique_id = f"eaton_battery_{description['key']}"
        self._attr_name = description["name"]
        self._native_min_value = float(description["min"])
        self._native_max_value = float(description["max"])
        self._native_step = float(description["step"])
        self._native_unit_of_measurement = description["unit"]
        self._attr_device_class = description["device_class"]

    @property
    def extra_state_attributes(self):
        # For power entities, show the wattage equivalent
        if self._key in ("charge_power", "discharge_power"):
            percent = self.native_value
            if percent is not None:
                try:
                    watts = int(round((percent / 100) * 3600))
                except Exception:
                    watts = None
                return {"wattage": watts}
        return None

    @property
    def native_min_value(self):
        return self._native_min_value

    @property
    def native_max_value(self):
        return self._native_max_value

    @property
    def native_step(self):
        return self._native_step

    @property
    def native_unit_of_measurement(self):
        return self._native_unit_of_measurement

    @property
    def native_value(self):
        # Get the value from hass.data storage
        return self.hass.data[DOMAIN]["number_values"].get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        # Store the value in hass.data
        self.hass.data[DOMAIN]["number_values"][self._key] = value
        self.async_write_ha_state()

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
