
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.storage import Store
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect
from .const import DOMAIN
from .number_constants import NUMBER_ENTITIES

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN]["coordinator"]
    store = Store(hass, 1, f"{DOMAIN}_number_values.json")
    # Load stored values or initialize
    stored = await store.async_load() or {}
    hass.data[DOMAIN]["number_values"] = stored
    hass.data[DOMAIN]["number_store"] = store
    entities = [
        EatonBatteryNumberEntity(hass, coordinator, desc)
        for desc in NUMBER_ENTITIES
    ]
    # Register all entities for dispatcher updates
    for entity in entities:
        entity._all_entities = entities
    async_add_entities(entities)

class EatonBatteryNumberEntity(CoordinatorEntity, NumberEntity):
    @property
    def mode(self):
        return "box"
    def __init__(self, hass, coordinator, description):
        super().__init__(coordinator)
        self.hass = hass
        self.coordinator = coordinator
        self._key = description["key"]
        self._attr_unique_id = f"eaton_battery_{description['key']}"
        self._attr_name = description["name"]
        self._native_min_value = float(description["min"])
        self._native_max_value = float(description["max"])
        self._native_step = float(description["step"])
        self._native_unit_of_measurement = description["unit"]
        self._attr_device_class = description["device_class"]
        self._all_entities = None

    async def async_added_to_hass(self):
        # Register for dispatcher updates
        async_dispatcher_connect(self.hass, f"{DOMAIN}_number_update", self._handle_external_update)

    def _handle_external_update(self):
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        # Show the linked value for power entities
        if self._key == "charge_power":
            percent = self.native_value
            if percent is not None:
                watts = int(round((percent / 100) * 3600))
                return {"wattage": watts}
        elif self._key == "charge_power_watt":
            watts = self.native_value
            if watts is not None:
                percent = int(round((watts / 3600) * 100))
                return {"percent": percent}
        elif self._key == "discharge_power":
            percent = self.native_value
            if percent is not None:
                watts = int(round((percent / 100) * 3600))
                return {"wattage": watts}
        elif self._key == "discharge_power_watt":
            watts = self.native_value
            if watts is not None:
                percent = int(round((watts / 3600) * 100))
                return {"percent": percent}
        return None

    @property
    def native_min_value(self):
        return self._native_min_value

    @property
    def native_max_value(self):
        return self._native_max_value

    @property
    def native_step(self):
        return self._native_step

    @property
    def native_unit_of_measurement(self):
        return self._native_unit_of_measurement

    @property
    def native_value(self):
        # Get the value from hass.data storage
        return self.hass.data[DOMAIN]["number_values"].get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        # Store the value and sync the linked value if needed
        self.hass.data[DOMAIN]["number_values"][self._key] = value
        linked_key = None
        if self._key == "charge_power":
            watts = int(round((value / 100) * 3600))
            self.hass.data[DOMAIN]["number_values"]["charge_power_watt"] = watts
            linked_key = "charge_power_watt"
        elif self._key == "charge_power_watt":
            percent = int(round((value / 3600) * 100))
            self.hass.data[DOMAIN]["number_values"]["charge_power"] = percent
            linked_key = "charge_power"
        elif self._key == "discharge_power":
            watts = int(round((value / 100) * 3600))
            self.hass.data[DOMAIN]["number_values"]["discharge_power_watt"] = watts
            linked_key = "discharge_power_watt"
        elif self._key == "discharge_power_watt":
            percent = int(round((value / 3600) * 100))
            self.hass.data[DOMAIN]["number_values"]["discharge_power"] = percent
            linked_key = "discharge_power"
        # Save to persistent storage
        await self.hass.data[DOMAIN]["number_store"].async_save(self.hass.data[DOMAIN]["number_values"])
        # Instantly update all number entities
        if linked_key and self._all_entities:
            for entity in self._all_entities:
                if entity._key == linked_key:
                    entity.async_write_ha_state()
        async_dispatcher_send(self.hass, f"{DOMAIN}_number_update")
        self.async_write_ha_state()

    @property
    def device_info(self):
        return self.coordinator.device_info
