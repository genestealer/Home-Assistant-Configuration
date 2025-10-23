import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import sensor, time as time_component, binary_sensor as bs
from esphome.const import (
    CONF_ID,
)
from . import EverbluComponent

CONF_CS_PIN = "cs_pin"
CONF_GDO0_PIN = "gdo0_pin"
CONF_ERROR_LED_PIN = "error_led_pin"
CONF_ERROR_LED_INVERTED = "error_led_inverted"
CONF_FREQUENCY = "frequency"
CONF_METER_SERIAL = "meter_serial"
CONF_METER_YEAR = "meter_year"
CONF_READ_AT_STARTUP = "read_at_startup"
CONF_READ_SCHEDULE = "read_schedule"
CONF_TIME_ID = "time_id"
CONF_BLINK_ON_FAILURE = "blink_on_failure"
CONF_SCAN_START = "scan_start_mhz"
CONF_SCAN_END = "scan_end_mhz"
CONF_DEEP_SCAN_START = "deep_scan_start_mhz"
CONF_DEEP_SCAN_END = "deep_scan_end_mhz"

CONF_LITERS = "liters"
CONF_BATTERY = "battery"
CONF_READS_COUNTER = "reads_counter"
CONF_RSSI = "rssi"
CONF_RSSI_DBM = "rssi_dbm"
CONF_LQI = "lqi"
CONF_TIME_START = "time_start"
CONF_TIME_END = "time_end"
CONF_DISCOVERED_FREQUENCY = "discovered_frequency"
CONF_RADIO_CONNECTED = "radio_connected"

SENSOR_SCHEMA = cv.Schema({
    cv.Optional(CONF_LITERS): sensor.sensor_schema(),
    cv.Optional(CONF_BATTERY): sensor.sensor_schema(),
    cv.Optional(CONF_READS_COUNTER): sensor.sensor_schema(),
    cv.Optional(CONF_RSSI): sensor.sensor_schema(),
    cv.Optional(CONF_RSSI_DBM): sensor.sensor_schema(),
    cv.Optional(CONF_LQI): sensor.sensor_schema(),
    cv.Optional(CONF_TIME_START): sensor.sensor_schema(),
    cv.Optional(CONF_TIME_END): sensor.sensor_schema(),
    cv.Optional(CONF_DISCOVERED_FREQUENCY): sensor.sensor_schema(),
    cv.Optional(CONF_RADIO_CONNECTED): bs.binary_sensor_schema(),
})

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(EverbluComponent),
    cv.Required(CONF_CS_PIN): pins.gpio_output_pin_schema,
    cv.Required(CONF_GDO0_PIN): pins.gpio_input_pin_schema,
    cv.Optional(CONF_ERROR_LED_PIN): pins.gpio_output_pin_schema,
    cv.Optional(CONF_ERROR_LED_INVERTED, default=False): cv.boolean,
    cv.Required(CONF_FREQUENCY): cv.float_,
    # Meter serial: 1..8 digits (as number). Reject 0 and > 99,999,999.
    cv.Required(CONF_METER_SERIAL): cv.All(cv.uint32_t, cv.int_range(min=1, max=99999999)),
    # Meter year: last two digits only (00..99)
    cv.Required(CONF_METER_YEAR): cv.All(cv.uint8_t, cv.int_range(min=0, max=99)),
    cv.Optional(CONF_READ_AT_STARTUP, default=True): cv.boolean,
    # Restrict schedule to known options to catch typos at compile time
    cv.Optional(CONF_READ_SCHEDULE, default="Monday-Friday"): cv.one_of("Monday-Friday", "Monday-Saturday", "Monday-Sunday"),
    cv.Optional(CONF_TIME_ID): cv.use_id(time_component.RealTimeClock),
    cv.Optional(CONF_BLINK_ON_FAILURE, default=True): cv.boolean,
    # Optional scan ranges for discovery (MHz). If omitted, defaults are used.
    cv.Optional(CONF_SCAN_START): cv.float_,
    cv.Optional(CONF_SCAN_END): cv.float_,
    cv.Optional(CONF_DEEP_SCAN_START): cv.float_,
    cv.Optional(CONF_DEEP_SCAN_END): cv.float_,
}).extend(SENSOR_SCHEMA).extend(cv.polling_component_schema("24h"))

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Pins
    cs = await cg.gpio_pin_expression(config[CONF_CS_PIN])
    gdo0 = await cg.gpio_pin_expression(config[CONF_GDO0_PIN])
    cg.add(var.set_cs_pin(cs))
    cg.add(var.set_gdo0_pin(gdo0))
    if (elp := config.get(CONF_ERROR_LED_PIN)) is not None:
        led = await cg.gpio_pin_expression(elp)
        cg.add(var.set_error_led_pin(led))
    if CONF_ERROR_LED_INVERTED in config:
        cg.add(var.set_error_led_inverted(config[CONF_ERROR_LED_INVERTED]))

    # Settings
    cg.add(var.set_frequency(config[CONF_FREQUENCY]))
    cg.add(var.set_meter_serial(config[CONF_METER_SERIAL]))
    cg.add(var.set_meter_year(config[CONF_METER_YEAR]))
    cg.add(var.set_read_schedule(config[CONF_READ_SCHEDULE]))
    cg.add(var.set_read_at_startup(config[CONF_READ_AT_STARTUP]))
    if CONF_TIME_ID in config:
        time_var = await cg.get_variable(config[CONF_TIME_ID])
        cg.add(var.set_time(time_var))
    if CONF_BLINK_ON_FAILURE in config:
        cg.add(var.set_blink_on_failure(config[CONF_BLINK_ON_FAILURE]))

    # Optional scan ranges
    has_scan = (CONF_SCAN_START in config) and (CONF_SCAN_END in config)
    has_deep = (CONF_DEEP_SCAN_START in config) and (CONF_DEEP_SCAN_END in config)
    if has_scan:
        cg.add(var.set_scan_range(config[CONF_SCAN_START], config[CONF_SCAN_END]))
    if has_deep:
        cg.add(var.set_deep_scan_range(config[CONF_DEEP_SCAN_START], config[CONF_DEEP_SCAN_END]))

    # Sensors
    if (lit := config.get(CONF_LITERS)) is not None:
        s = await sensor.new_sensor(lit)
        cg.add(var.set_liters_sensor(s))
    if (bat := config.get(CONF_BATTERY)) is not None:
        s = await sensor.new_sensor(bat)
        cg.add(var.set_battery_sensor(s))
    if (rc := config.get(CONF_READS_COUNTER)) is not None:
        s = await sensor.new_sensor(rc)
        cg.add(var.set_reads_counter_sensor(s))
    if (r := config.get(CONF_RSSI)) is not None:
        s = await sensor.new_sensor(r)
        cg.add(var.set_rssi_sensor(s))
    if (rd := config.get(CONF_RSSI_DBM)) is not None:
        s = await sensor.new_sensor(rd)
        cg.add(var.set_rssi_dbm_sensor(s))
    if (lqi := config.get(CONF_LQI)) is not None:
        s = await sensor.new_sensor(lqi)
        cg.add(var.set_lqi_sensor(s))
    if (ts := config.get(CONF_TIME_START)) is not None:
        s = await sensor.new_sensor(ts)
        cg.add(var.set_time_start_sensor(s))
    if (te := config.get(CONF_TIME_END)) is not None:
        s = await sensor.new_sensor(te)
        cg.add(var.set_time_end_sensor(s))
    if (df := config.get(CONF_DISCOVERED_FREQUENCY)) is not None:
        s = await sensor.new_sensor(df)
        cg.add(var.set_discovered_frequency_sensor(s))
    if (rb := config.get(CONF_RADIO_CONNECTED)) is not None:
        b = await bs.new_binary_sensor(rb)
        cg.add(var.set_radio_connected_binary_sensor(b))
