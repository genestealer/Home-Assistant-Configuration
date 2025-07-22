import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class EatonXstorageHomeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="Eaton xStorage Home",
            update_interval=timedelta(minutes=1),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            response = await self.api.get_status()
            return response.get("result", {})  # Extract only the 'result' part
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")