"""PodPointEntity class"""

from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from podpointclient.charge_mode import ChargeMode
from podpointclient.charge_override import ChargeOverride
from podpointclient.pod import Pod
from podpointclient.schedule import Schedule

from .const import (
    APP_IMAGE_URL_BASE,
    ATTR_STATE,
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_CHARGING,
    ATTR_STATE_CONNECTED_WAITING,
    ATTR_STATE_IDLE,
    ATTR_STATE_PENDING,
    ATTR_STATE_RANKING,
    ATTR_STATE_SUSPENDED_EV,
    ATTR_STATE_SUSPENDED_EVSE,
    ATTR_STATE_WAITING,
    ATTRIBUTION,
    CHARGING_FLAG,
    DOMAIN,
    NAME,
)
from .coordinator import PodPointDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class PodPointEntity(CoordinatorEntity):
    """Pod Point Entity"""

    def __init__(
        self,
        coordinator: PodPointDataUpdateCoordinator,
        config_entry: ConfigEntry,
        idx: int,
    ):
        super().__init__(coordinator)
        self.pod_id = idx
        self.config_entry = config_entry
        self.extra_attrs = {}

        self.__update_attrs()

    def __update_attrs(self):
        pod: Pod = self.pod

        attrs = {
            "attribution": ATTRIBUTION,
            "id": pod.id,
            "integration": DOMAIN,
            "suggested_area": "Outside",
            "total_kwh": pod.total_kwh,
            "total_charge_seconds": pod.total_charge_seconds,
            "current_kwh": pod.current_kwh,
            "charge_mode": pod.charge_mode,
        }

        attrs.update(pod.dict)

        state = None
        for status in pod.statuses:
            state = self.compare_state(state, status.key_name)

        is_available_state = (state == ATTR_STATE_AVAILABLE) or (
            state == ATTR_STATE_IDLE
        )
        is_charging_state = state == ATTR_STATE_CHARGING
        is_override_charge_mode = pod.charge_mode == ChargeMode.OVERRIDE
        is_manual_charge_mode = pod.charge_mode == ChargeMode.MANUAL
        charging_not_allowed = self.charging_allowed is False
        should_be_waiting_state = is_available_state and charging_not_allowed
        should_be_connected_waiting_state = is_charging_state and charging_not_allowed
        should_be_available = is_available_state and (
            is_override_charge_mode or is_manual_charge_mode
        )
        should_be_charging = is_charging_state and (
            is_override_charge_mode or is_manual_charge_mode
        )
        should_be_suspended_ev = is_charging_state and (
            pod.charging_state == ATTR_STATE_SUSPENDED_EV
        )
        should_be_suspended_evse = is_charging_state and (
            pod.charging_state == ATTR_STATE_SUSPENDED_EVSE
        )
        should_be_pending = (
            self.coordinator.last_message_at is not None
            and self.pod.last_message_at is not None
            and self.coordinator.last_message_at > self.pod.last_message_at
        )

        if should_be_waiting_state:
            state = ATTR_STATE_WAITING

        if should_be_connected_waiting_state:
            state = ATTR_STATE_CONNECTED_WAITING

        # Pod should be available if pod is available and state is overriden, or manual charge mode
        if should_be_available:
            state = ATTR_STATE_AVAILABLE

        # Pod should be charging if pod is charging and state is overriden, or manual charge mode
        if should_be_charging:
            state = ATTR_STATE_CHARGING

        # Pod should be suspended evse if pod is charging and connectivity status is suspended evse
        if should_be_suspended_evse:
            state = ATTR_STATE_SUSPENDED_EVSE

        # Pod should be suspended ev if pod is charging and connectivity status is suspended ev
        if should_be_suspended_ev:
            state = ATTR_STATE_SUSPENDED_EV

        # Should this pod be pending?
        if should_be_pending:
            state = ATTR_STATE_PENDING

        attrs[ATTR_STATE] = state

        self._attr_state = state

        self.extra_attrs = attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.__update_attrs()
        self.async_write_ha_state()

    @property
    def pod(self) -> Pod:
        """Return the underlying pod that drives this entity"""
        pod: Pod = self.coordinator.data[self.pod_id]
        return pod

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        if self.pod.id:
            return f"{DOMAIN}_{self.pod.id}_{self.pod.ppid}"

        return self.config_entry.entry_id

    @property
    def available(self) -> bool:
        typed_coordinator: PodPointDataUpdateCoordinator = self.coordinator
        return typed_coordinator.online is True

    @property
    def device_info(self) -> Dict[str, Any]:
        name = NAME
        if len(self.psl) > 0:
            name = self.psl

        dictionary = {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": name,
            "model": self.model,
            "manufacturer": NAME,
        }

        if self.firmware_version:
            dictionary["sw_version"] = self.firmware_version

        return dictionary

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self.extra_attrs

    @property
    def charging_allowed(self) -> bool:
        """Is charging allowed by schedule?"""
        pod: Pod = self.coordinator.data[self.pod_id]
        schedules: List[Schedule] = pod.charge_schedules
        override: ChargeOverride = pod.charge_override

        # Are we in 'manual' mode?
        if pod.charge_mode == ChargeMode.MANUAL:
            return True

        # No schedules are found, we will assume we can charge
        if len(schedules) <= 0:
            return True

        # If there is a charge override in place, we can charge
        if override is not None and override.active:
            return True

        weekday = datetime.today().weekday() + 1
        schedule_for_day: Schedule = next(
            (schedule for schedule in schedules if schedule.start_day == weekday),
            None,
        )

        # If no schedule is set for our day, return False early, there should always be a
        # schedule for each day, even if it is inactive
        if schedule_for_day is None:
            return False

        schedule_active = schedule_for_day.is_active

        # If schedule_active is None, there was a problem. we will return False
        if schedule_active is None:
            return False

        # If the schedule for this day is not active, we can charge
        if schedule_active is False:
            return True

        def to_int(stringy_int):
            return int(stringy_int)

        start_time = list(map(to_int, schedule_for_day.start_time.split(":")))
        start_date = datetime.now().replace(
            hour=start_time[0], minute=start_time[1], second=start_time[2]
        )

        end_time = list(map(to_int, schedule_for_day.end_time.split(":")))
        end_day = schedule_for_day.end_day
        end_date = None
        if end_day < weekday:
            # roll into next week
            end_time = end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )

            # How many days do we add to the current date to get to the desired end day?
            day_offset = (7 - weekday) + (end_day - 1)
            end_date = end_time + timedelta(days=day_offset)
        elif end_day > weekday:
            day_offset = end_day - weekday

            end_time = end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )
            end_date = end_time + timedelta(days=day_offset)
        else:
            end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )

        # Problem creating the end_date, so we will exit with False
        if end_date is None:
            return False

        in_range = start_date <= datetime.now() <= end_date

        # Are we within the range for today?
        return in_range

    @property
    def unit_id(self) -> int:
        """Return the unit id - used for schedule updates"""
        return self.pod.unit_id

    @property
    def psl(self) -> str:
        """Return the PSL - used for identifying multiple pods"""
        return self.pod.ppid

    @property
    def model(self) -> str:
        """Return the model of our podpoint"""
        return self.pod.model.name

    @property
    def firmware_version(self) -> str:
        """Return the pod's firmware version"""
        firmware = None

        if self.pod.firmware and self.pod.firmware.version_info:
            firmware = self.pod.firmware.version_info.manifest_id

        return firmware

    @property
    def serial_number(self) -> str:
        """Return the serial number, or ppid"""
        serial_number: str = self.pod.ppid

        if self.pod.firmware:
            serial_number = self.pod.firmware.serial_number

        return serial_number

    @property
    def image(self) -> str:
        """Return the image url for this model"""
        return self.__pod_image(self.model)

    @property
    def connected(self) -> bool:
        """Returns true if pod is connected to a vehicle"""
        status = self.extra_state_attributes.get(ATTR_STATE, "")
        return status in (
            CHARGING_FLAG,
            ATTR_STATE_CONNECTED_WAITING,
            ATTR_STATE_SUSPENDED_EV,
            ATTR_STATE_SUSPENDED_EVSE,
        )

    @staticmethod
    def compare_state(state, pod_state) -> str:
        """Given two states, which one is most important"""
        ranking = ATTR_STATE_RANKING

        state_sanitized = state.lower().replace("_", "-") if state is not None else None
        pod_state_sanitized = (
            pod_state.lower().replace("_", "-") if pod_state is not None else None
        )

        # If pod state is None, but state is set, return the state
        if pod_state_sanitized is None and state_sanitized is not None:
            return state_sanitized

        if state_sanitized is None and pod_state_sanitized is not None:
            return pod_state_sanitized

        try:
            state_rank = ranking.index(state_sanitized)
        except ValueError:
            state_rank = 100

        try:
            pod_rank = ranking.index(pod_state_sanitized)
        except ValueError:
            pod_rank = 100

        winner = state_sanitized if state_rank >= pod_rank else pod_state_sanitized
        return winner

    def __pod_image(self, model: str) -> str:
        if model is None:
            return None

        model_slug = self.__model_slug()
        model_type = model_slug[0]
        model_id = model_slug[1]

        if model_type == "UP":
            model_type = "UC"

        if model_type == "1C":
            model_type = "2C"

        img = model_type

        if model_id == "03":
            img = f"{model_type}-{model_id}"

        if model_id == "05":
            img = "UC-05"

        return f"{APP_IMAGE_URL_BASE}/{img.lower()}.png"

    def __model_slug(self) -> List[str]:
        return self.model.upper()[3:8].split("-")

    @staticmethod
    def _td_format(td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ("year", 60 * 60 * 24 * 365),
            ("month", 60 * 60 * 24 * 30),
            ("day", 60 * 60 * 24),
            ("hour", 60 * 60),
            ("minute", 60),
            ("second", 1),
        ]

        strings = []
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                has_s = "s" if period_value > 1 else ""
                strings.append(f"{period_value} {period_name}{has_s}")

        output = "0s"
        if len(strings) > 0:
            output = ", ".join(strings)

        return output
