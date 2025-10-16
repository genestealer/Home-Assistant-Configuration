# ESPHome Common Configurations

This directory contains shared configuration files that are included by device-specific YAML files to ensure consistency across all ESPHome devices.

## File Descriptions

### Core Files

- **`device_base.yaml`** - Base configuration for all devices (API, OTA, restart button, status sensors)
- **`device_base_wifi.yaml`** - Wi-Fi configuration and diagnostic sensors
- **`status_led.yaml`** - Status LED configuration (can be excluded with `!remove`)

### Sensor Modules

- **`bme280.yaml`** - BME280 sensor (temperature, humidity, pressure, dew point, altitude)
- **`pms5003t.yaml`** - PMS5003T particulate matter sensor
- **`daqi.yaml`** - UK Daily Air Quality Index calculation

## Usage

Include these files in your device configuration using:

```yaml
packages:
  device_base: !include common/device_base.yaml
  wifi: !include common/device_base_wifi.yaml
  status_led: !include common/status_led.yaml  # Optional
  bme280: !include common/bme280.yaml        # If using BME280
  pms5003t: !include common/pms5003t.yaml    # If using PMS5003T
  daqi: !include common/daqi.yaml           # For air quality index
```

## Required Substitutions

Each device must define these substitution variables:

### Core Required

- `name`: Device name (lowercase, hyphens only)
- `friendly_name`: Human-readable device name
- `ui_comment`: Description shown in ESPHome dashboard
- `ip`, `gateway`, `subnet`: Network configuration
- `project_name`: Unique project identifier
- `project_version`: Version number
- `package_import_url`: GitHub import URL
- `log_level`: Logging level (DEBUG, INFO, WARN, ERROR)
- `sensor_update_interval`: General sensor update frequency
- `wifi_sensor_update_interval`: Wi-Fi diagnostic update frequency

### Status LED (if using)

- `status_led`: GPIO pin for status LED
- `status_led_inverted`: "true" or "false"

### BME280 (if using)

- `i2c_pin_sda`, `i2c_pin_scl`: I2C pins
- `i2c_scan`, `i2c_frequency`: I2C settings
- `bme280_i2c_address`: Sensor I2C address
- `bme280_update_interval`: Update frequency
- `bme280_offset_temperature`: Temperature calibration offset

### PMS5003T (if using)

- `pmsx003_pin_rx`, `pmsx003_pin_tx`: UART pins
- `pmsx003_baud_rate`: Communication speed
- `pmsx003_reset_pin_num`: Reset pin
- `pmsx003_update_interval`: Update frequency
- `pmsx003_type`: Sensor model

## Best Practices

1. **Entity Categories**: Diagnostic sensors should use `entity_category: "diagnostic"`
2. **Device Classes**: Always specify appropriate `device_class` for sensors
3. **State Classes**: Use `measurement` for regularly changing values, `total_increasing` for counters
4. **Update Intervals**: Balance between data freshness and system load
5. **Filtering**: Use `throttle`, `delta`, and `heartbeat` to optimize data transmission

## Version History

- **v1.0.0** - Initial modular structure
- **v1.1.0** - Added entity categories and improved device classes
- **v1.2.0** - Enhanced BME280 with dew point and altitude calculations
