import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.helpers import entity_registry as er
from homeassistant.const import SERVICE_RELOAD
import voluptuous as vol

from .api import EatonBatteryAPI
from .coordinator import EatonXstorageHomeCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "number", "button", "switch"]

# List of PV-related sensor keys that should be disabled when has_pv=False
PV_SENSOR_KEYS = [
    "status.energyFlow.acPvRole",
    "status.energyFlow.acPvValue", 
    "status.energyFlow.dcPvRole",
    "status.energyFlow.dcPvValue",
    "status.last30daysEnergyFlow.photovoltaicProduction",
    "status.today.photovoltaicProduction",
    "device.inverterNominalVpv",
    "technical_status.pv1Voltage",
    "technical_status.pv1Current",
    "technical_status.pv2Voltage",
    "technical_status.pv2Current",
    "technical_status.dcCurrentInjectionR",
    "technical_status.dcCurrentInjectionS",
    "technical_status.dcCurrentInjectionT",
]


async def async_setup(hass: HomeAssistant, config: dict):
    return True  # Not used for config flow-based setup

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Setting up Eaton xStorage Home from config entry.")
    api = EatonBatteryAPI(
        username=entry.data["username"],
        password=entry.data["password"],
        inverter_sn=entry.data["inverter_sn"],
        email=entry.data["email"],
        hass=hass,
        host=entry.data["host"],
        app_id="com.eaton.xstoragehome",
        name="Eaton xStorage Home",
        manufacturer="Eaton"
    )
    await api.connect()
    coordinator = EatonXstorageHomeCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )

    # Run initial PV sensor migration for existing installations
    await async_migrate_pv_sensors(hass, entry)

    # Add update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    async def reload_service_handler(call):
        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)

    hass.services.async_register(
        DOMAIN, SERVICE_RELOAD, reload_service_handler, schema=vol.Schema({})
    )

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options and handle PV sensor migration."""
    # Handle PV sensor enabling/disabling based on has_pv setting
    await async_migrate_pv_sensors(hass, entry)
    
    # Reload the integration to apply new settings
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_pv_sensors(hass: HomeAssistant, entry: ConfigEntry):
    """Enable or disable PV sensors based on has_pv configuration."""
    entity_registry = er.async_get(hass)
    has_pv = entry.data.get("has_pv", False)
    
    _LOGGER.info(f"Migrating PV sensors: has_pv={has_pv}")
    
    for sensor_key in PV_SENSOR_KEYS:
        entity_id = f"sensor.eaton_xstorage_{sensor_key.replace('.', '_')}"
        
        # Try to find the entity in the registry
        registry_entry = entity_registry.async_get(entity_id)
        if registry_entry:
            # Update the entity's enabled state based on PV configuration
            entity_registry.async_update_entity(
                entity_id, 
                disabled_by=None if has_pv else er.RegistryEntryDisabler.INTEGRATION
            )
            _LOGGER.debug(f"{'Enabled' if has_pv else 'Disabled'} PV sensor: {entity_id}")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    results = [
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    ]
    return all(results)
