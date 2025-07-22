"""Binary sensor platform for pod_point."""

import logging
from typing import Any, Dict

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import EntityCategory

from .const import ATTR_CONNECTION_STATE_ONLINE, ATTR_STATE, ATTRIBUTION, DOMAIN
from .coordinator import PodPointDataUpdateCoordinator
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Handle coordinator offline on boot - no data will be populated
    if coordinator.online is False:
        return

    sensors = []
    for i in range(len(coordinator.data)):
        cable_sensor = PodPointCableConnectionSensor(coordinator, entry, i)
        cable_sensor.pod_id = i
        sensors.append(cable_sensor)

        cloud_sensor = PodPointCloudConnectionSensor(coordinator, entry, i)
        cloud_sensor.pod_id = i
        sensors.append(cloud_sensor)

    async_add_devices(sensors)


class PodPointCableConnectionSensor(PodPointEntity, BinarySensorEntity):
    """pod_point cable connection class."""

    _attr_has_entity_name = True
    _attr_name = "Cable Status"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    @property
    def unique_id(self):
        return f"{super().unique_id}_cable_status"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.connected


class PodPointCloudConnectionSensor(PodPointEntity, BinarySensorEntity):
    """pod_point cloud connection class."""

    _attr_has_entity_name = True
    _attr_name = "Cloud Connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        return f"{super().unique_id}_cloud_connection"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        if self.pod is None:
            return False

        if self.pod.connectivity_status is None:
            return False

        return (
            self.pod.connectivity_status.connectivity_status
            == ATTR_CONNECTION_STATE_ONLINE
        )

    @property
    def icon(self):
        """Return the icon of the sensor."""

        if self.is_on:
            return "mdi:cloud-check-variant"

        return "mdi:cloud-off"
