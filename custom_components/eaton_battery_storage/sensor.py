# pyright: ignore[reportMissingImports]
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    # status endpoint
    "status.currentMode.command": {"name": "Current Mode Command", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.duration": {"name": "Current Mode Duration", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.startTime": {"name": "Current Mode Start Time", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.endTime": {"name": "Current Mode End Time", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.recurrence": {"name": "Current Mode Recurrence", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.type": {"name": "Current Mode Type", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.parameters.action": {"name": "Current Mode Action", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.parameters.power": {"name": "Current Mode Power", "unit": None, "device_class": None, "entity_category": None},
    "status.currentMode.parameters.soc": {"name": "Current Mode SOC", "unit": PERCENTAGE, "device_class": "battery", "entity_category": None},
    "status.energyFlow.acPvRole": {"name": "AC PV Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.acPvValue": {"name": "AC PV Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.batteryBackupLevel": {"name": "Battery Backup Level", "unit": PERCENTAGE, "device_class": "battery", "entity_category": None},
    "status.energyFlow.batteryStatus": {"name": "Battery Status", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "status.energyFlow.batteryEnergyFlow": {"name": "Battery Power", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.criticalLoadRole": {"name": "Critical Load Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.criticalLoadValue": {"name": "Critical Load Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.dcPvRole": {"name": "DC PV Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.dcPvValue": {"name": "DC PV Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.gridRole": {"name": "Grid Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.gridValue": {"name": "Grid Power", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.nonCriticalLoadRole": {"name": "Non-Critical Load Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.nonCriticalLoadValue": {"name": "Non-Critical Load Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.operationMode": {"name": "Operation Mode", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.selfConsumption": {"name": "Self Consumption", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.selfSufficiency": {"name": "Self Sufficiency", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.energyFlow.stateOfCharge": {"name": "Battery State of Charge", "unit": PERCENTAGE, "device_class": "battery", "entity_category": None},
    "status.energyFlow.energySavingModeEnabled": {"name": "Energy Saving Mode Enabled", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.energySavingModeActivated": {"name": "Energy Saving Mode Activated", "unit": None, "device_class": None, "entity_category": None},
    "status.last30daysEnergyFlow.gridConsumption": {"name": "30 Days Grid Consumption", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.last30daysEnergyFlow.photovoltaicProduction": {"name": "30 Days PV Production", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.last30daysEnergyFlow.selfConsumption": {"name": "30 Days Self Consumption", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.last30daysEnergyFlow.selfSufficiency": {"name": "30 Days Self Sufficiency", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.today.gridConsumption": {"name": "Today's Grid Consumption", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.today.photovoltaicProduction": {"name": "Today's PV Production", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.today.selfConsumption": {"name": "Today's Self Consumption", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.today.selfSufficiency": {"name": "Today's Self Sufficiency", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    # device endpoint
    "device.firmwareVersion": {"name": "Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterFirmwareVersion": {"name": "Inverter Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.bmsFirmwareVersion": {"name": "BMS Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.energySavingMode.houseConsumptionThreshold": {"name": "House Consumption Threshold", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": EntityCategory.DIAGNOSTIC},

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
        self._entity_category = description["entity_category"]
    @property
    def entity_category(self):
        return self._entity_category

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
            # If value is still a dict, return None
            if isinstance(value, dict):
                return None
            # Format startTime and endTime to 12-hour format if applicable
            if self._key.endswith("startTime") or self._key.endswith("endTime"):
                if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                    # Accept both int and string representations
                    time_val = int(value)
                    hour = time_val // 100
                    minute = time_val % 100
                    if 0 <= hour < 24 and 0 <= minute < 60:
                        suffix = "am" if hour < 12 or hour == 24 else "pm"
                        hour12 = hour % 12
                        if hour12 == 0:
                            hour12 = 12
                        return f"{hour12}:{minute:02d}{suffix}"
            return value
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
