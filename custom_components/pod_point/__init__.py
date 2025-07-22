"""
Custom integration to integrate pod_point with Home Assistant.

For more details about this integration, please refer to
https://github.com/mattrayner/pod-point-home-assistant-component
"""

import asyncio
from datetime import timedelta
import logging
from pathlib import Path
from typing import Dict, List

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from podpointclient.charge import Charge
from podpointclient.client import PodPointClient
from podpointclient.pod import Pod

from .const import (
    APP_IMAGE_URL_BASE,
    CONF_EMAIL,
    CONF_HTTP_DEBUG,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_HTTP_DEBUG,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import PodPointDataUpdateCoordinator
from .services import async_deregister_services, async_register_services

_LOGGER: logging.Logger = logging.getLogger(__package__)

# pylint: disable=unused-argument


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    # If data for pod_point is not setup, prime it
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)

    # If http debug is set, use that, or default
    try:
        http_debug = entry.options[CONF_HTTP_DEBUG]
    except KeyError:
        http_debug = DEFAULT_HTTP_DEBUG

    client = PodPointClient(
        username=email, password=password, session=session, http_debug=http_debug
    )

    # If a scan interval is set, use that, or default
    try:
        scan_interval = timedelta(seconds=entry.options[CONF_SCAN_INTERVAL])
    except KeyError:
        scan_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=scan_interval
    )

    # Check the credentials we have and ensure that we can perform a refresh
    await coordinator.async_config_entry_first_refresh()

    # Given a successful inital refresh, store this coordinator for this specific config entry
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup static image asset serving
    should_cache = False
    files_path = Path(__file__).parent / "static"
    if hass.http:
        await hass.http.async_register_static_paths(
            [StaticPathConfig(APP_IMAGE_URL_BASE, str(files_path), should_cache)]
        )

    # For every platform defined, check if the user has disabled it. If not, set it up
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)

    await hass.config_entries.async_forward_entry_setups(entry, coordinator.platforms)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register the services
    await async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ],
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    unloaded = await async_unload_entry(hass, entry)
    if unloaded is False:
        _LOGGER.error("Error unloading entry: %s", entry)

    await async_setup_entry(hass, entry)
