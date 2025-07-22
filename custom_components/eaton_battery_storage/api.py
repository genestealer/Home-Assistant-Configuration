import aiohttp
import logging
from datetime import datetime, timedelta
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

class EatonBatteryAPI:
    def __init__(self, hass, host, username, password, app_id, name, manufacturer):
        self.hass = hass
        self.host = host
        self.username = username
        self.password = password
        self.app_id = app_id
        self.name = name
        self.manufacturer = manufacturer
        self.access_token = None
        self.token_expiration = None
        self.store = Store(hass, 1, f"{host}_token")

    async def connect(self):
        url = f"https://{self.host}/api/auth/signin"
        payload = {
            "username": self.username,
            "pwd": self.password,
            "userType": "customer"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, ssl=False) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("successful") and "token" in result.get("result", {}):
                        self.access_token = result["result"]["token"]
                        self.token_expiration = datetime.utcnow() + timedelta(minutes=55)
                        await self.store_token()
                        _LOGGER.info("Connected successfully. Bearer token acquired.")
                    elif "error" in result:
                        err = result["error"]
                        err_msg = err.get("description") or err.get("errCode") or "Authentication failed"
                        raise ValueError(err_msg)
                    else:
                        _LOGGER.warning(f"Authentication failed: {result}")
                        raise ValueError("Authentication failed with unexpected response.")
            except Exception as e:
                _LOGGER.error(f"Error during authentication: {e}")
                raise

    async def store_token(self):
        await self.store.async_save({
            "access_token": self.access_token,
            "token_expiration": self.token_expiration.isoformat() if self.token_expiration else None
        })

    async def load_token(self):
        data = await self.store.async_load()
        if data:
            self.access_token = data.get("access_token")
            expiration_str = data.get("token_expiration")
            if expiration_str:
                self.token_expiration = datetime.fromisoformat(expiration_str)

    async def refresh_token(self):
        _LOGGER.info("Refreshing access token...")
        await self.connect()

    async def ensure_token_valid(self):
        if not self.access_token or not self.token_expiration or datetime.utcnow() >= self.token_expiration:
            _LOGGER.info("Token missing or expired. Re-authenticating...")
            await self.refresh_token()

    async def make_request(self, method, endpoint, **kwargs):
        await self.ensure_token_valid()

        url = f"https://{self.host}{endpoint}"
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers
        kwargs["ssl"] = False

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status == 401:
                        _LOGGER.warning("Access token expired. Refreshing token...")
                        await self.refresh_token()
                        headers["Authorization"] = f"Bearer {self.access_token}"
                        kwargs["headers"] = headers
                        async with session.request(method, url, **kwargs) as retry_response:
                            return await retry_response.json()
                    return await response.json()
            except Exception as e:
                _LOGGER.error(f"Error during API request to {endpoint}: {e}")
                return {}

    async def get_status(self):
        return await self.make_request("GET", "/api/device/status")