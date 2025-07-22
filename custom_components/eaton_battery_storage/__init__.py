import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.const import SERVICE_RELOAD
import voluptuous as vol

from .api import EatonBatteryAPI
from .coordinator import EatonXstorageHomeCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    return True  # Not used for config flow-based setup

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Setting up Eaton xStorage Home from config entry.")
    api = EatonBatteryAPI(
        username=entry.data["username"],
        password=entry.data["password"],
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

    async def reload_service_handler(call):
        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)

    hass.services.async_register(
        DOMAIN, SERVICE_RELOAD, reload_service_handler, schema=vol.Schema({})
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
