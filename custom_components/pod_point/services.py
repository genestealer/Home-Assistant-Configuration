"""Services for the Pod Point integration."""

from datetime import datetime
import logging
from typing import List

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from podpointclient.client import PodPointClient
from podpointclient.pod import Pod
import pytz
import voluptuous as vol

from .const import (
    ATTR_CONFIG_ENTRY_ID,
    ATTR_HOURS,
    ATTR_MINUTES,
    ATTR_SECONDS,
    DOMAIN,
    SERVICE_CHARGE_NOW,
    SERVICE_STOP_CHARGE_NOW,
)
from .coordinator import PodPointDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class PodPointServiceException(Exception):
    """Exception for Pod Point services."""


async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for the Pod Point integration, if not registered yet."""

    if hass.services.has_service(DOMAIN, SERVICE_CHARGE_NOW):
        return
    else:
        _LOGGER.info("Registering SERVICE_CHARGE_NOW for Pod Point integration")

        async def async_charge_now_service(call: ServiceCall):
            coordinator = await get_coordinator(hass, call.data[ATTR_CONFIG_ENTRY_ID])
            await handle_charge_now(hass, coordinator, call)

        hass.services.async_register(
            DOMAIN,
            SERVICE_CHARGE_NOW,
            async_charge_now_service,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
                    vol.Optional(ATTR_HOURS): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=24)
                    ),
                    vol.Optional(ATTR_MINUTES): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=59)
                    ),
                    vol.Optional(ATTR_SECONDS): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=59)
                    ),
                }
            ),
        )

    if hass.services.has_service(DOMAIN, SERVICE_STOP_CHARGE_NOW):
        return
    else:
        _LOGGER.info("Registering SERVICE_STOP_CHARGE_NOW for Pod Point integration")

        async def async_stop_charge_now_service(call: ServiceCall):
            coordinator = await get_coordinator(hass, call.data[ATTR_CONFIG_ENTRY_ID])
            await handle_stop_charge_now(hass, coordinator, call)

        hass.services.async_register(
            DOMAIN,
            SERVICE_STOP_CHARGE_NOW,
            async_stop_charge_now_service,
            schema=vol.Schema({vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string}),
        )


async def async_deregister_services(hass: HomeAssistant) -> None:
    """Deregister services for the Pod Point integration"""

    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_NOW)

    hass.services.async_remove(DOMAIN, SERVICE_STOP_CHARGE_NOW)


async def get_coordinator(
    hass: HomeAssistant, config_entry_id: str
) -> PodPointDataUpdateCoordinator:
    """Get the right Pod Point Data Coordinator based on the device id, else get the default one."""
    if config_entry_id not in hass.data[DOMAIN]:
        raise ValueError(f"Config entry with id {config_entry_id} not found!")

    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][config_entry_id]
    return coordinator


async def handle_charge_now(
    hass: HomeAssistant, coordinator: PodPointDataUpdateCoordinator, call: ServiceCall
) -> None:
    """Handle the call for the add_product service."""
    api: PodPointClient = coordinator.api
    pods: List[Pod] = coordinator.pods
    pod: Pod
    if len(pods) == 1:
        pod = pods[0]
    else:
        PodPointServiceException(
            f"Service only supports accounts with 1 Pod attached, found {len(pods)} Pods!"
        )

    hours = call.data.get(ATTR_HOURS, 0)
    minutes = call.data.get(ATTR_MINUTES, 0)
    seconds = call.data.get(ATTR_SECONDS, 0)

    hours_set = 0 < hours <= 24
    minutes_set = 0 < minutes <= 59
    seconds_set = 0 < seconds <= 59
    valid_time_passed = hours_set or minutes_set or seconds_set

    if valid_time_passed is False:
        raise PodPointServiceException(
            "Please pass an hours, minutes or seconds value. Cannot set 'charge now' with 0 values."
        )

    await api.async_set_charge_override(
        pod=pod, hours=hours, minutes=minutes, seconds=seconds
    )

    coordinator.last_message_at = datetime.now(pytz.UTC)
    await coordinator.async_request_refresh()


async def handle_stop_charge_now(
    hass: HomeAssistant, coordinator: PodPointDataUpdateCoordinator, call: ServiceCall
) -> None:
    """Handle the call for the add_product service."""
    api: PodPointClient = coordinator.api
    pods: List[Pod] = coordinator.pods
    pod: Pod
    if len(pods) == 1:
        pod = pods[0]
    else:
        PodPointServiceException(
            f"Service only supports accounts with 1 Pod attached, found {len(pods)} Pods!"
        )

    await api.async_delete_charge_override(pod=pod)

    coordinator.last_message_at = datetime.now(pytz.UTC)
    await coordinator.async_request_refresh()
