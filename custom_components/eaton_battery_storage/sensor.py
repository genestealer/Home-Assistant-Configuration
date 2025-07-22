import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "currentMode.command": {"name": "Current Mode Command", "unit": None, "device_class": None},
    "energyFlow.acPvRole": {"name": "AC PV Role", "unit": None, "device_class": None},
    "energyFlow.acPvValue": {"name": "AC PV Value", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.batteryBackupLevel": {"name": "Battery Backup Level", "unit": PERCENTAGE, "device_class": "battery"},
    "energyFlow.batteryStatus": {"name": "Battery Status", "unit": None, "device_class": None},
    "energyFlow.batteryEnergyFlow": {"name": "Battery Power", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.criticalLoadRole": {"name": "Critical Load Role", "unit": None, "device_class": None},
    "energyFlow.criticalLoadValue": {"name": "Critical Load Value", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.dcPvRole": {"name": "DC PV Role", "unit": None, "device_class": None},
    "energyFlow.dcPvValue": {"name": "DC PV Value", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.gridRole": {"name": "Grid Role", "unit": None, "device_class": None},
    "energyFlow.gridValue": {"name": "Grid Power", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.nonCriticalLoadRole": {"name": "Non-Critical Load Role", "unit": None, "device_class": None},
    "energyFlow.nonCriticalLoadValue": {"name": "Non-Critical Load Value", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.operationMode": {"name": "Operation Mode", "unit": None, "device_class": None},
    "energyFlow.selfConsumption": {"name": "Self Consumption", "unit": UnitOfPower.WATT, "device_class": "power"},
    "energyFlow.selfSufficiency": {"name": "Self Sufficiency", "unit": PERCENTAGE, "device_class": None},
    "energyFlow.stateOfCharge": {"name": "Battery State of Charge", "unit": PERCENTAGE, "device_class": "battery"},
    "energyFlow.energySavingModeEnabled": {"name": "Energy Saving Mode Enabled", "unit": None, "device_class": None},
    "energyFlow.energySavingModeActivated": {"name": "Energy Saving Mode Activated", "unit": None, "device_class": None},
    "last30daysEnergyFlow.gridConsumption": {"name": "30 Days Grid Consumption", "unit": UnitOfPower.WATT, "device_class": "power"},
    "last30daysEnergyFlow.photovoltaicProduction": {"name": "30 Days PV Production", "unit": UnitOfPower.WATT, "device_class": "power"},
    "last30daysEnergyFlow.selfConsumption": {"name": "30 Days Self Consumption", "unit": PERCENTAGE, "device_class": None},
    "last30daysEnergyFlow.selfSufficiency": {"name": "30 Days Self Sufficiency", "unit": PERCENTAGE, "device_class": None},
    "today.gridConsumption": {"name": "Today's Grid Consumption", "unit": UnitOfPower.WATT, "device_class": "power"},
    "today.photovoltaicProduction": {"name": "Today's PV Production", "unit": UnitOfPower.WATT, "device_class": "power"},
    "today.selfConsumption": {"name": "Today's Self Consumption", "unit": PERCENTAGE, "device_class": None},
    "today.selfSufficiency": {"name": "Today's Self Sufficiency", "unit": PERCENTAGE, "device_class": None},
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    entities = [EatonXStorageSensor(coordinator, key, description) for key, description in SENSOR_TYPES.items()]
    async_add_entities(entities)

class EatonXStorageSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, description):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._key = key
        self._name = description["name"]
        self._unit = description["unit"]
        self._device_class = description["device_class"]

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"eaton_xstorage_{self._key}"

    @property
    def state(self):
        try:
            keys = self._key.split(".")
            value = self.coordinator.data
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, {})
                else:
                    value = {}
            return value if value != {} else None
        except Exception as e:
            _LOGGER.error(f"Error retrieving state for {self._key}: {e}")
            return None

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class

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
