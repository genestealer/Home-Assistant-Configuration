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
            # Fetch all endpoints in parallel
            results = {}
            status = await self.api.get_status()
            device = await self.api.get_device()
            config_state = await self.api.get_config_state()
            settings = await self.api.get_settings()
            metrics = await self.api.get_metrics()
            metrics_daily = await self.api.get_metrics_daily()
            schedule = await self.api.get_schedule()
            # The following may require technician account, handle errors gracefully
            try:
                technical_status = await self.api.get_technical_status()
            except Exception:
                technical_status = None
            try:
                maintenance_diagnostics = await self.api.get_maintenance_diagnostics()
            except Exception:
                maintenance_diagnostics = None

            results["status"] = status.get("result", {}) if status else {}
            results["device"] = device.get("result", {}) if device else {}
            results["config_state"] = config_state if config_state else {}
            results["settings"] = settings.get("result", {}) if settings else {}
            results["metrics"] = metrics if metrics else {}
            results["metrics_daily"] = metrics_daily if metrics_daily else {}
            results["schedule"] = schedule if schedule else {}
            results["technical_status"] = technical_status.get("result", {}) if technical_status else {}
            results["maintenance_diagnostics"] = maintenance_diagnostics.get("result", {}) if maintenance_diagnostics else {}

            return results
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")