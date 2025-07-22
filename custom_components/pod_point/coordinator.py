"""
Data coordinator for pod point client
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, List, Set, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from podpointclient.charge import Charge
from podpointclient.client import PodPointClient
from podpointclient.errors import ApiConnectionError, AuthError, SessionError
from podpointclient.pod import Firmware, Pod
from podpointclient.user import User
import pytz

from .const import DOMAIN, LIMITED_POD_INCLUDES

_LOGGER: logging.Logger = logging.getLogger(__package__)


class PodPointDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    _firmware_refresh_interval = 5  # How many refreshes between a firmware update call

    def __init__(
        self, hass: HomeAssistant, client: PodPointClient, scan_interval: timedelta
    ) -> None:
        """Initialize."""
        self.api: PodPointClient = client
        self.platforms = []
        self.pods: List[Pod] = []
        self.home_charges: List[Charge] = []
        self.charges_perpage_all = (
            50  # When we are fetching all charges (new pod, or first launch)
        )
        self.charges_perpage_update = (
            3  # Fetching an update, unlikely to change from poll to poll by more than 1
        )
        self.pod_dict = None
        self.online = None
        self.firmware_refresh = 1  # Initial refresh will be a firmware refresh too, ensuring we pull firmware for all pods at startup
        self.user: User = None
        self.last_message_at = datetime(1970, 1, 1, 0, 0, 0, 0, pytz.UTC)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=scan_interval)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            _LOGGER.debug("Updating pods and charges")
            new_pods: List[Pod] = []
            self.pod_dict: Dict[int, Pod] = None

            self.user = await self.api.async_get_user()

            new_pods = await self.__async_update_pods()

            _LOGGER.debug(
                "=== POD UPDATE ===\nFound Pods: %s\nPrevious Pods: %s",
                len(new_pods),
                len(self.pods),
            )

            # Group Pods by ID so that we can organise our charges into the pods
            # they were performed on
            new_pods_by_id = self.__group_pods_by_unit_id(pods=new_pods)

            (new_pods, new_pods_by_id) = await self.__async_group_pods(
                new_pods, new_pods_by_id
            )

            new_pods_by_id = self.__group_pods_by_unit_id(pods=new_pods)

            # Fetch firmware data for pods, if it is needed
            self.firmware_refresh -= 1
            if self.firmware_refresh <= 0:
                new_pods_by_id = await self.__async_refresh_firmware(
                    new_pods, new_pods_by_id
                )

            # Fetch connection status data for pods
            new_pods_by_id = await self.__async_update_pod_connection_status(
                new_pods_by_id
            )

            # Determine if we should fetch for all charges, or just the most recent for a user.
            should_fetch_all_charges = self.__should_fetch_all_charges(
                new_pods=new_pods
            )

            # Fetch a list of new charges
            new_charges: List[Charge] = await self.__fetch_home_charges(
                all_charges=should_fetch_all_charges
            )

            # We will filter out any of the new charges from the existing list. This will
            # ensure any overlap is not duplicated.
            new_charge_ids: Set(int) = set([charge.id for charge in new_charges])
            combined_home_charges: List[Charge] = new_charges + [
                charge
                for charge in self.home_charges
                if charge.id not in new_charge_ids
            ]

            _LOGGER.debug(
                "=== CHARGE UPDATE ===\nShould get all charges: %s\nPrevious Charges: %s\n\
Updated Charges: %s\nCombined Charges: %s",
                should_fetch_all_charges,
                len(self.home_charges),
                len(new_charges),
                len(combined_home_charges),
            )

            # Store charges for next refresh
            self.home_charges = combined_home_charges

            # Create a dictionary so that we can track the last charge for each
            # pod, used o calculate the cost of the last charge
            last_completed_charges_dict: Dict[str, Charge] = {}
            for key in new_pods_by_id:
                last_completed_charges_dict[key] = None

            for charge in combined_home_charges:
                unit_id = charge.pod.id
                pod: Pod = new_pods_by_id.get(unit_id, None)

                if pod is None:
                    continue

                pod.charges.append(charge)
                pod.total_kwh = pod.total_kwh + charge.kwh_used
                pod.total_charge_seconds = pod.total_charge_seconds + charge.duration

                charge_cost = charge.energy_cost or 0
                pod.total_cost = pod.total_cost + charge_cost

                # If this charge has an end (is not currently active)
                if charge.ends_at is not None:
                    # If either there is no 'last charge' for this pod, or this charge
                    # is more recent than the last one we found, set the last charge
                    # cost and update our dictionary
                    if last_completed_charges_dict.get(pod.unit_id, None) is None or (
                        charge.ends_at
                        > last_completed_charges_dict[pod.unit_id].ends_at
                        and charge.energy_cost is not None
                    ):
                        last_completed_charges_dict[pod.unit_id] = charge
                        setattr(pod, "last_charge_cost", charge.energy_cost)
                else:
                    pod.current_kwh = charge.kwh_used

            self.pods = list(new_pods_by_id.values())

            if self.online is False:
                _LOGGER.info("Connection to Pod Point re-established.")
            self.online = True

            return self.pods  # sets coordinator.data

        except ApiConnectionError as exception:
            if self.online is not False:
                _LOGGER.warning("Unable to connect to Pod Point. (%s)", exception)

            self.online = False
            _LOGGER.debug(exception)

            raise UpdateFailed(
                "Unable to connect to Pod Point. Retrying"
            ) from exception

        except (AuthError, SessionError) as exception:
            _LOGGER.debug("Recommending re-auth: %s", exception)

            raise ConfigEntryAuthFailed(
                "There was a problem logging in with your account."
            ) from exception
        except Exception as exception:
            _LOGGER.warning(
                "Recieved an unexpected exception when updating data from Pod Point. \
If this issue persists, please contact the developer."
            )
            _LOGGER.exception(exception)
            raise UpdateFailed() from exception

    def __group_pods_by_unit_id(self, pods: List[Pod] = None) -> Dict[int, Pod]:
        """Given a list of pods, will return a dictionary { pod.unit_id: pod, *** }.
        If no pods are passed, will perfom on self.pods"""
        pod_dict: Dict[int, Pod] = {}

        if pods is None:
            pods = self.pods

        for pod in pods:
            pod_dict[pod.unit_id] = pod

        self.pod_dict = pod_dict
        return self.pod_dict

    async def __fetch_home_charges(self, all_charges: bool = True) -> List[Charge]:
        """Fetch either all charges for a user, or progressively paginate until you have the latest
        set of charges. Filtered to only include 'home' charges"""
        charges: List[Charge] = []

        if all_charges:
            charges = await self.api.async_get_all_charges(
                perpage=self.charges_perpage_all
            )
        else:
            # Fetch charges until we have the most recent ones found, should reduce load
            # on the Pod Point servers
            last_charge_ids: List[int] = [
                pod.charges[0].id
                for pod in self.pods
                if (len(pod.charges) > 0) and pod.charges[0].id is not None
            ]
            charges: List[Charge] = []

            page = 1
            while len(last_charge_ids) > 0:
                page_charges = await self.api.async_get_charges(
                    perpage=self.charges_perpage_update, page=page
                )

                # We should not get to a page with no charges before finding all the charges in our
                # list. If we do then go boom. Will cause HA to show an error updating data.
                if len(page_charges) == 0:
                    raise Exception(
                        f"Attempting to update charges and recieved a 0 page when we were \
expecting more charges. Page {page}, looking for : {last_charge_ids}"
                    )

                # Process charges left to right, adding them to the 'back' of our charges
                # list until we hit one of the charges we are looking for.
                for charge in page_charges:
                    if charge.id is None:
                        continue

                    if charge.id not in last_charge_ids:
                        charges.append(charge)
                        continue

                    last_charge_ids.remove(charge.id)
                    charges.append(charge)

                    if len(last_charge_ids) == 0:
                        break

                page += 1

        home_charges: List[Charge] = list(
            filter(lambda charge: charge.location.home is True, charges)
        )

        return home_charges

    def __should_fetch_all_charges(self, new_pods: List[Pod]) -> bool:
        """Given a list of new pods, should we query for all charges on a users account,
        or just the most recent"""
        fetch_all_charges = False
        if len(new_pods) == len(self.pods):  # There are the same number of pods
            fetch_all_charges = not self.__pods_match(new_pods=new_pods)
        else:  # There are more (or less) pods than we previously had
            fetch_all_charges = True

        return fetch_all_charges

    def __combine_pods(self, new_pods_by_id: Dict[str, Pod]) -> List[Pod]:
        """Given a new set of pods, combine them with the existing pod data to create a new list"""
        new_pods: List[Pod] = []

        for previous_pod in self.pods:
            new_pod = new_pods_by_id[previous_pod.unit_id]
            new_pod.price = previous_pod.price
            new_pod.model = previous_pod.model
            new_pod.unit_connectors = previous_pod.unit_connectors
            new_pod.firmware = previous_pod.firmware

            new_pods.append(new_pod)

        return new_pods

    def __pods_match(self, new_pods: List[Pod]) -> bool:
        set1 = set((pod.id) for pod in self.pods)
        difference = [pod for pod in new_pods if (pod.id) not in set1]

        # Is there a difference in the pod IDs?
        return len(difference) == 0

    def __process_repair_notification(
        self, hass: HomeAssistant, firmware: Firmware, pod: Pod
    ):
        if firmware.update_available:
            ir.async_create_issue(
                hass,
                DOMAIN,
                "firmware_update",
                is_fixable=False,
                is_persistent=False,
                learn_more_url="https://pod-point.com/electric-car-news",
                severity="other",
                translation_key="firmware_update",
                translation_placeholders={"ppid": pod.ppid},
            )
        else:
            ir.async_delete_issue(hass, DOMAIN, "firmware_update")

    async def __async_update_pods(self) -> List[Pod]:
        # Should we get a limited set of data (subsiquent refreshes)
        if len(self.pods) > 0:
            _LOGGER.debug("Existing pods found, performing a limited data pull")
            return await self.api.async_get_all_pods(includes=LIMITED_POD_INCLUDES)
        else:
            _LOGGER.debug("No existing pods found, performing a full data pull")
            return await self.api.async_get_all_pods()

    async def __async_group_pods(
        self, new_pods, new_pods_by_id
    ) -> Tuple[List[Pod], Dict[str, Pod]]:
        # Attempt to update our new pods with additional data from the existing pods.
        # This allows us to query less data each refresh, kinder on the Pod Point APIs.
        if self.__pods_match(new_pods=new_pods):
            # Created an updated list of pods combining old and new data
            _LOGGER.debug("Combining new and old pods")
            new_pods = self.__combine_pods(new_pods_by_id=new_pods_by_id)
            new_pods_by_id = self.__group_pods_by_unit_id(pods=new_pods)
        elif (
            len(self.pods) > 0
        ):  # Ensure that we are not re-querying if this is he first run
            _LOGGER.debug(
                "New pods from Pod Point do not match those saved. Performing a full data pull."
            )
            new_pods = await self.api.async_get_all_pods()

        return (new_pods, new_pods_by_id)

    async def __async_refresh_firmware(
        self, new_pods: List[Pod], new_pods_by_id: Dict[str, Pod]
    ) -> Dict[str, Pod]:
        _LOGGER.debug("=== FIRMWARE STATUS UPDATE ===")

        for pod in new_pods:
            pod_firmwares: List[Firmware] = await self.api.async_get_firmware(pod=pod)

            if len(pod_firmwares) <= 0:
                _LOGGER.warning(
                    "Unable to retrive firmware information for Pod %s",
                    pod.ppid,
                )
            else:
                for firmware in pod_firmwares:
                    self.__process_repair_notification(
                        hass=self.hass, firmware=firmware, pod=pod
                    )

                    # Populate the firmware of the pod
                    pod.firmware = firmware
                    new_pods_by_id[pod.unit_id] = pod

        self.firmware_refresh = self._firmware_refresh_interval

        return new_pods_by_id

    async def __async_update_pod_connection_status(
        self, new_pods_by_id: Dict[str, Pod]
    ) -> Dict[str, Pod]:
        _LOGGER.debug("=== POD CONNECTION STATUS UPDATE ===")

        # flat_pods = [item for row in new_pods_by_id.values() for item in row]
        # Fetch connection status for each pod
        for pod in new_pods_by_id.values():
            connectivity_status = await self.api.async_get_connectivity_status(pod=pod)

            if connectivity_status is not None:
                pod.connectivity_status = connectivity_status
                pod.last_message_at = connectivity_status.last_message_at
                pod.charging_state = connectivity_status.charging_state

                if pod.charging_state is not None:
                    pod.charging_state = pod.charging_state.lower().replace("_", "-")

                new_pods_by_id[pod.unit_id] = pod

        return new_pods_by_id
