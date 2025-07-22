# Number platform constants for Eaton Battery Storage

CHARGE_END_SOC = "charge_end_soc"
CHARGE_POWER = "charge_power"
CHARGE_DURATION = "charge_duration"
DISCHARGE_END_SOC = "discharge_end_soc"
DISCHARGE_POWER = "discharge_power"
DISCHARGE_DURATION = "discharge_duration"

NUMBER_ENTITIES = [
    {
        "key": CHARGE_END_SOC,
        "name": "Charge End SOC",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
        "device_class": "battery",
    },
    {
        "key": CHARGE_POWER,
        "name": "Charge Power",
        "min": 5,
        "max": 100,
        "step": 1,
        "unit": "%",
        "device_class": "power",
    },
    {
        "key": CHARGE_DURATION,
        "name": "Charge Duration",
        "min": 1,
        "max": 12,
        "step": 1,
        "unit": "h",
        "device_class": "duration",
    },
    {
        "key": DISCHARGE_END_SOC,
        "name": "Discharge End SOC",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
        "device_class": "battery",
    },
    {
        "key": DISCHARGE_POWER,
        "name": "Discharge Power",
        "min": 5,
        "max": 100,
        "step": 1,
        "unit": "%",
        "device_class": "power",
    },
    {
        "key": DISCHARGE_DURATION,
        "name": "Discharge Duration",
        "min": 1,
        "max": 12,
        "step": 1,
        "unit": "h",
        "device_class": "duration",
    },
]
