import logging
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Eaton xStorage Home switches from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    entities = [
        EatonXStoragePowerSwitch(coordinator)
    ]
    async_add_entities(entities)

class EatonXStoragePowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control the power state of the Eaton xStorage Home device."""
    
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_entity_category = EntityCategory.CONFIG
        self._optimistic_state = None  # For optimistic updates

    @property
    def name(self):
        """Return the name of the switch."""
        return "Inverter Power"

    @property
    def unique_id(self):
        """Return the unique ID of the switch."""
        return "eaton_xstorage_inverter_power"

    @property
    def icon(self):
        """Return the icon for the switch."""
        return "mdi:power"

    @property
    def device_info(self):
        """Return device information."""
        return self.coordinator.device_info

    @property
    def is_on(self):
        """Return true if the device is on."""
        # If we have an optimistic state from a recent command, use that
        if self._optimistic_state is not None:
            return self._optimistic_state
            
        try:
            # Otherwise, check the powerState from device data
            device_data = self.coordinator.data.get("device", {}) if self.coordinator.data else {}
            return device_data.get("powerState", False)
        except (AttributeError, TypeError, KeyError):
            return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        try:
            # Set optimistic state immediately for responsive UI
            self._optimistic_state = True
            self.async_write_ha_state()
            
            result = await self.coordinator.api.set_device_power(True)
            
            if result.get("successful"):
                _LOGGER.info("Successfully turned on Eaton xStorage Home device")
                # Wait a bit for the device to actually change state
                await asyncio.sleep(3)
            else:
                _LOGGER.warning(f"API call completed but may not have succeeded: {result}")
                # Still wait a bit in case it worked despite the response
                await asyncio.sleep(2)
            
            # Always refresh the coordinator data after attempting to change power state
            await self.coordinator.async_request_refresh()
            
            # Clear optimistic state so we use real data
            self._optimistic_state = None
            
        except Exception as e:
            _LOGGER.error(f"Error turning on device: {e}")
            # Clear optimistic state and refresh to get current state
            self._optimistic_state = None
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        try:
            # Set optimistic state immediately for responsive UI
            self._optimistic_state = False
            self.async_write_ha_state()
            
            result = await self.coordinator.api.set_device_power(False)
            
            if result.get("successful"):
                _LOGGER.info("Successfully turned off Eaton xStorage Home device")
                # Wait a bit for the device to actually change state
                await asyncio.sleep(3)
            else:
                _LOGGER.warning(f"API call completed but may not have succeeded: {result}")
                # Still wait a bit in case it worked despite the response
                await asyncio.sleep(2)
            
            # Always refresh the coordinator data after attempting to change power state
            await self.coordinator.async_request_refresh()
            
            # Clear optimistic state so we use real data
            self._optimistic_state = None
            
        except Exception as e:
            _LOGGER.error(f"Error turning off device: {e}")
            # Clear optimistic state and refresh to get current state
            self._optimistic_state = None
            await self.coordinator.async_request_refresh()

    @property
    def should_poll(self):
        """No polling needed since we use coordinator."""
        return False

    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        # Clear optimistic state when we get real data from coordinator
        if self._optimistic_state is not None:
            self._optimistic_state = None
        super()._handle_coordinator_update()
