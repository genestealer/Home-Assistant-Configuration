"""Constants for pod_point."""

from podpointclient.version import __version__ as pod_point_client_version

from .version import __version__ as integration_version

# Base component constants
NAME = "Pod Point"
DOMAIN = "pod_point"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = integration_version
ATTRIBUTION = "Data provided by https://pod-point.com/"
ISSUE_URL = "https://github.com/mattrayner/pod-point-home-assistant-component/issues"

# Icons
ICON_1C = "mdi:ev-plug-type1"
ICON_2C = "mdi:ev-plug-type2"
ICON = ICON_2C
ICON_EV_STATION = "mdi:ev-station"

SWITCH_ICON = ICON_EV_STATION

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
UPDATE = "update"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH, UPDATE]
ENERGY = "energy"

SERVICE_CHARGE_NOW = "charge_now"
SERVICE_STOP_CHARGE_NOW = "stop_charge_now"

# Configuration and options
CONF_ENABLED = "enabled"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300
CONF_HTTP_DEBUG = "http_debug"
DEFAULT_HTTP_DEBUG = False
CONF_CURRENCY = "currency"
DEFAULT_CURRENCY = "GBP"

# Defaults
DEFAULT_NAME = DOMAIN

# State attributes
ATTR_ID = "pod_id"
ATTR_PSL = "psl"
ATTR_HOME = "home"
ATTR_PAYG = "payg"
ATTR_PUBLIC = "public"
ATTR_EVZONE = "ev_zone"
ATTR_LAT = "lat"
ATTR_LNG = "lng"
ATTR_UNIT_ID = "unit_id"
ATTR_COMMISSIONED = "date_commissioned"
ATTR_CREATED = "date_created"
ATTR_LAST_CONTACT = "last_contacted_at"
ATTR_CONTACTLESS_ENABLED = "contactless_enabled"
ATTR_TIMEZONE = "timezone"
ATTR_MODEL = "model"
ATTR_PRICE = "price"
ATTR_STATUS = "status"
ATTR_STATUS_KEY_NAME = "key_name"
ATTR_STATUS_NAME = "name"
ATTR_STATUS_LABEL = "label"
ATTR_STATUS_DOOR = "door"
ATTR_STATUS_DOOR_ID = "door_id"
ATTR_CONNECTOR = "connector"
ATTR_CONNECTOR_ID = "id"
ATTR_CONNECTOR_DOOR = "door"
ATTR_CONNECTOR_DOOR_ID = "door_id"
ATTR_CONNECTOR_POWER = "power"
ATTR_CONNECTOR_CURRENT = "current"
ATTR_CONNECTOR_VOLTAGE = "voltage"
ATTR_CONNECTOR_CHARGE_METHOD = "charge_method"
ATTR_CONNECTOR_HAS_CABLE = "has_cable"
ATTR_CONNECTOR_SOCKET = "socket"
ATTR_CONNECTOR_SOCKET_TYPE = "type"
ATTR_CONNECTOR_SOCKET_OCPP_NAME = "ocpp_name"
ATTR_CONNECTOR_SOCKET_OCPP_CODE = "ocpp_code"
ATTR_STATE = "state"
ATTR_IMAGE = "local_image"

ATTR_STATE_AVAILABLE = "available"
ATTR_STATE_UNAVAILABLE = "unavailable"
ATTR_STATE_CHARGING = "charging"
ATTR_STATE_IDLE = "idle"
ATTR_STATE_SUSPENDED_EV = "suspended-ev"
ATTR_STATE_SUSPENDED_EVSE = "suspended-evse"
ATTR_STATE_PENDING = "pending"
ATTR_STATE_OUT_OF_SERVICE = "out-of-service"
ATTR_STATE_WAITING = "waiting-for-schedule"
ATTR_STATE_CONNECTED_WAITING = "connected-waiting-for-schedule"
ATTR_STATE_CHARGE_OVERRIED = "charge-override"
ATTR_STATE_RANKING = [
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_UNAVAILABLE,
    ATTR_STATE_IDLE,
    ATTR_STATE_CHARGING,
    ATTR_STATE_SUSPENDED_EV,
    ATTR_STATE_OUT_OF_SERVICE,
    ATTR_STATE_SUSPENDED_EVSE,
]
ATTR_CONNECTION_STATE_ONLINE = "ONLINE"

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_HOURS = "hours"
ATTR_MINUTES = "minutes"
ATTR_SECONDS = "seconds"

# Flags
CHARGING_FLAG = ATTR_STATE_CHARGING

# API Details
BASE_API_VERSION = "v4"
BASE_API_URL = "https://api.pod-point.com/" + BASE_API_VERSION

# Image serving
APP_IMAGE_URL_BASE = f"/api/{DOMAIN}/static"

# Pod refresh includes
LIMITED_POD_INCLUDES = ["statuses", "charge_schedules", "charge_override"]

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION} (podpointclient={pod_point_client_version})
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
