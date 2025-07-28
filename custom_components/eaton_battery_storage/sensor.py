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
    "status.energyFlow.acPvRole": {"name": "AC PV Role", "unit": None, "device_class": None, "entity_category": None, "pv_related": True},
    "status.energyFlow.acPvValue": {"name": "AC PV Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None, "pv_related": True},
    "status.energyFlow.batteryBackupLevel": {"name": "Battery Backup Level", "unit": PERCENTAGE, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "status.energyFlow.batteryStatus": {"name": "Battery Status", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "status.energyFlow.batteryEnergyFlow": {"name": "Battery Power", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.criticalLoadRole": {"name": "Critical Load Role", "unit": None, "device_class": None, "entity_category": None},
    "status.energyFlow.criticalLoadValue": {"name": "Critical Load Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.energyFlow.dcPvRole": {"name": "DC PV Role", "unit": None, "device_class": None, "entity_category": None, "pv_related": True},
    "status.energyFlow.dcPvValue": {"name": "DC PV Value", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None, "pv_related": True},
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
    "status.last30daysEnergyFlow.photovoltaicProduction": {"name": "30 Days PV Production", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None, "pv_related": True},
    "status.last30daysEnergyFlow.selfConsumption": {"name": "30 Days Self Consumption", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.last30daysEnergyFlow.selfSufficiency": {"name": "30 Days Self Sufficiency", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.today.gridConsumption": {"name": "Today's Grid Consumption", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None},
    "status.today.photovoltaicProduction": {"name": "Today's PV Production", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": None, "pv_related": True},
    "status.today.selfConsumption": {"name": "Today's Self Consumption", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    "status.today.selfSufficiency": {"name": "Today's Self Sufficiency", "unit": PERCENTAGE, "device_class": None, "entity_category": None},
    # device endpoint
    "device.firmwareVersion": {"name": "Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterFirmwareVersion": {"name": "Inverter Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.bmsFirmwareVersion": {"name": "BMS Firmware Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.energySavingMode.houseConsumptionThreshold": {"name": "House Consumption Threshold", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterManufacturer": {"name": "Inverter Manufacturer", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterModelName": {"name": "Inverter Model Name", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterVaRating": {"name": "Inverter VA Rating", "unit": "VA", "device_class": "apparent_power", "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterSerialNumber": {"name": "Inverter Serial Number", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.inverterNominalVpv": {"name": "Inverter Nominal VPV", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC, "pv_related": True},
    "device.bmsCapacity": {"name": "BMS Capacity", "unit": "kWh", "device_class": "energy_storage", "entity_category": EntityCategory.DIAGNOSTIC},
    "device.bmsSerialNumber": {"name": "BMS Serial Number", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.bmsModel": {"name": "BMS Model", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.bundleVersion": {"name": "Bundle Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.localPortalRemoteId": {"name": "Local Portal Remote ID", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.dns": {"name": "DNS Server", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "device.timezone.name": {"name": "Device Timezone", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    # technical status endpoint - requires technician account
    "technical_status.operationMode": {"name": "Technical Operation Mode", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.gridVoltage": {"name": "Grid Voltage", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.gridFrequency": {"name": "Grid Frequency", "unit": "Hz", "device_class": "frequency", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.currentToGrid": {"name": "Current To Grid", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.inverterPower": {"name": "Inverter Power", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.inverterTemperature": {"name": "Inverter Temperature", "unit": "°C", "device_class": "temperature", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.busVoltage": {"name": "Bus Voltage", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.gridCode": {"name": "Grid Code", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.dcCurrentInjectionR": {"name": "DC Current Injection R", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.dcCurrentInjectionS": {"name": "DC Current Injection S", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.dcCurrentInjectionT": {"name": "DC Current Injection T", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.inverterModel": {"name": "Technical Inverter Model", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.inverterPowerRating": {"name": "Technical Inverter Power Rating", "unit": UnitOfPower.WATT, "device_class": "power", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.pv1Voltage": {"name": "PV1 Voltage", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC, "pv_related": True},
    "technical_status.pv1Current": {"name": "PV1 Current", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC, "pv_related": True},
    "technical_status.pv2Voltage": {"name": "PV2 Voltage", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC, "pv_related": True},
    "technical_status.pv2Current": {"name": "PV2 Current", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC, "pv_related": True},
    "technical_status.bmsVoltage": {"name": "BMS Voltage", "unit": "V", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsCurrent": {"name": "BMS Current", "unit": "A", "device_class": "current", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsTemperature": {"name": "BMS Temperature", "unit": "°C", "device_class": "temperature", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsAvgTemperature": {"name": "BMS Average Temperature", "unit": "°C", "device_class": "temperature", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsMaxTemperature": {"name": "BMS Max Temperature", "unit": "°C", "device_class": "temperature", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsMinTemperature": {"name": "BMS Min Temperature", "unit": "°C", "device_class": "temperature", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsTotalCharge": {"name": "BMS Total Charge", "unit": "kWh", "device_class": "energy", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsTotalDischarge": {"name": "BMS Total Discharge", "unit": "kWh", "device_class": "energy", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsStateOfCharge": {"name": "Technical BMS State of Charge", "unit": PERCENTAGE, "device_class": "battery", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsState": {"name": "BMS State", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsFaultCode": {"name": "BMS Fault Code", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsHighestCellVoltage": {"name": "BMS Highest Cell Voltage", "unit": "mV", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsLowestCellVoltage": {"name": "BMS Lowest Cell Voltage", "unit": "mV", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.bmsCellVoltageDelta": {"name": "BMS Cell Voltage Delta", "unit": "mV", "device_class": "voltage", "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.tidaProtocolVersion": {"name": "TIDA Protocol Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "technical_status.invBootloaderVersion": {"name": "Inverter Bootloader Version", "unit": None, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    # maintenance diagnostics endpoint - requires technician account  
    "maintenance_diagnostics.ramUsage.total": {"name": "System RAM Total", "unit": "MB", "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "maintenance_diagnostics.ramUsage.used": {"name": "System RAM Used", "unit": "MB", "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},
    "maintenance_diagnostics.cpuUsage.used": {"name": "System CPU Usage", "unit": PERCENTAGE, "device_class": None, "entity_category": EntityCategory.DIAGNOSTIC},

}

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    has_pv = config_entry.data.get("has_pv", False)
    
    # Create sensors based on PV configuration
    entities = []
    for key, description in SENSOR_TYPES.items():
        # Skip PV-related sensors if has_pv is False
        if description.get("pv_related", False) and not has_pv:
            continue
        entities.append(EatonXStorageSensor(coordinator, key, description, has_pv))
    
    async_add_entities(entities)

class EatonXStorageSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, description, has_pv):
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
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added.
        
        This only applies when first added to the entity registry.
        """
        # Disable TIDA Protocol Version by default as it's rarely useful
        if self._key == "technical_status.tidaProtocolVersion":
            return False
        return True

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"eaton_xstorage_{self._key}"

    @property
    def state(self):
        try:
            # Calculate BMS cell voltage delta first (before normal data extraction)
            if self._key == "technical_status.bmsCellVoltageDelta":
                try:
                    tech_status = self.coordinator.data.get("technical_status", {})
                    highest = tech_status.get("bmsHighestCellVoltage")
                    lowest = tech_status.get("bmsLowestCellVoltage")
                    
                    if highest is not None and lowest is not None:
                        delta = float(highest) - float(lowest)
                        result = round(delta, 1)
                        return result
                    else:
                        _LOGGER.debug(f"Delta calculation failed - missing values. Highest: {highest}, Lowest: {lowest}")
                        return None
                except (ValueError, TypeError) as e:
                    _LOGGER.error(f"Error calculating BMS cell voltage delta: {e}")
                    return None
            
            # Normal data extraction for other sensors
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
            # Convert RAM usage from bytes to megabytes
            if "ramUsage" in self._key and isinstance(value, (int, float)):
                return round(value / 1024 / 1024, 2)
            # Round CPU usage to 2 decimal places
            if "cpuUsage.used" in self._key and isinstance(value, (int, float)):
                return round(value, 2)
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
        return self.coordinator.device_info
    @property
    def should_poll(self):
        return False
