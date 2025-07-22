"""Support for Pod Point sensors."""

from __future__ import annotations

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityDescription,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PodPointDataUpdateCoordinator
from .entity import PodPointEntity

PARALLEL_UPDATES = 0

UPDATE_ENTITY_TYPES = UpdateEntityDescription(
    key="version",
    name="Firmware update",
    device_class=UpdateDeviceClass.FIRMWARE,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup update platform."""
    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Handle coordinator offline on boot - no data will be populated
    if coordinator.online is False:
        return

    for i in range(len(coordinator.data)):
        async_add_entities(
            [PodUpdateEntity(coordinator, UPDATE_ENTITY_TYPES, entry, i)]
        )


class PodUpdateEntity(PodPointEntity, UpdateEntity):
    """Representation of a Pod Update entity."""

    coordinator: PodPointDataUpdateCoordinator
    _attr_has_entity_name = True
    _attr_supported_features = UpdateEntityFeature.RELEASE_NOTES
    _attr_device_class: UpdateDeviceClass | None = UpdateDeviceClass.FIRMWARE
    _attr_release_summary: str | None = "A new firmware release is available."
    _attr_translation_key: str | None = "firmware_update"

    def __init__(
        self,
        coordinator: PodPointDataUpdateCoordinator,
        description: UpdateEntityDescription,
        config_entry: ConfigEntry,
        idx: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry, idx)
        self.coordinator = coordinator
        self.pod_id = idx
        self.config_entry = config_entry
        self.entity_description = description

    @property
    def unique_id(self):
        return f"{super().unique_id}_update"

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        return self.pod.firmware.firmware_version

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        return (
            f"{self.pod.firmware.firmware_version}_UPDATE_AVAILABLE"
            if self.pod.firmware.update_available
            else self.installed_version
        )

    @property
    def pod(self):
        return self.coordinator.data[self.pod_id]

    def release_notes(self) -> str | None:
        """Return full release notes."""
        return (
            f"A firmware update is available for {self.pod.ppid}."
            "\n\nExternal updating is not supported by the PodPoint APIs,"
            " please check the PodPoint mobile app for next steps."
            if self.pod.firmware.update_available
            else f"{self.pod.ppid} is up to date!"
        )
