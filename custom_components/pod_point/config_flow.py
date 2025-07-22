"""Adds config flow for Pod Point."""

import logging
from typing import Dict

from homeassistant import config_entries
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.device_registry import format_mac
from podpointclient.client import PodPointClient
import voluptuous as vol

from .const import (
    CONF_CURRENCY,
    CONF_EMAIL,
    CONF_HTTP_DEBUG,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_CURRENCY,
    DEFAULT_HTTP_DEBUG,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class PodPointFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Pod Point."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    # pylint: disable=unused-argument
    async def async_step_reauth(self, user_input: Dict[str, str] = None) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: Dict[str, str] = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_step_user(self, user_input: Dict[str, str] = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is None:
            user_input = {}
            # Provide defaults for form
            user_input[CONF_EMAIL] = ""
            user_input[CONF_PASSWORD] = ""

            return await self._show_config_form(user_input)

        valid = await self._test_credentials(
            user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
        )

        if valid is False:
            self._errors["base"] = "auth"
            return await self._show_config_form(user_input)

        existing_entry = await self.async_set_unique_id(user_input[CONF_EMAIL].lower())

        # If an entry exists, update it and show the re-auth message
        if existing_entry:
            self.hass.config_entries.async_update_entry(
                existing_entry, title=user_input[CONF_EMAIL], data=user_input
            )
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(title=user_input[CONF_EMAIL], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> FlowResult:
        return PodPointOptionsFlowHandler(config_entry)

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> FlowResult:
        formatted_mac = format_mac(discovery_info.macaddress)
        _LOGGER.info("Found PodPoint device with mac %s", formatted_mac)

        await self.async_set_unique_id(formatted_mac)
        self._abort_if_unique_id_configured()

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        return await self.async_step_user()

    async def _show_config_form(
        self, user_input: Dict[str, str]
    ) -> FlowResult:  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input[CONF_EMAIL]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username: str, password: str) -> bool:
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = PodPointClient(
                username=username, password=password, session=session
            )
            return await client.async_credentials_verified()
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class PodPointOptionsFlowHandler(config_entries.OptionsFlow):
    """Pod Point config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, _=None
    ) -> FlowResult:  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        currency_schema = {
            vol.Required(
                CONF_CURRENCY,
                default=self.options.get(CONF_CURRENCY, DEFAULT_CURRENCY),
            ): str
        }

        poll_schema = {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): int
        }

        platforms_schema = {
            vol.Required(
                x,
                default=self.options.get(x, True),
            ): bool
            for x in sorted(PLATFORMS)
        }

        debug_schema = {
            vol.Required(
                CONF_HTTP_DEBUG,
                default=self.options.get(CONF_HTTP_DEBUG, DEFAULT_HTTP_DEBUG),
            ): bool
        }

        options_schema = vol.Schema(
            {**currency_schema, **platforms_schema, **debug_schema, **poll_schema}
        )

        return self.async_show_form(step_id="user", data_schema=options_schema)

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL), data=self.options
        )
