import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from .api import EatonBatteryAPI

_LOGGER = logging.getLogger(__name__)

class EatonXStorageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eaton xStorage Home."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input["host"]
            username = user_input["username"]
            password = user_input["password"]

            api = EatonBatteryAPI(
                hass=self.hass,
                host=host,
                username=username,
                password=password,
                app_id="com.eaton.xstoragehome",
                name="Eaton xStorage Home",
                manufacturer="Eaton"
            )

            try:
                await api.connect()
                return self.async_create_entry(title="Eaton xStorage", data=user_input)
            except ValueError as e:
                _LOGGER.warning(f"Authentication failed: {e}")
                errors["base"] = str(e)
            except Exception as e:
                _LOGGER.error(f"Unexpected error: {e}")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )