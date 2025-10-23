import esphome.codegen as cg

AUTO_LOAD = ["sensor", "binary_sensor"]
DEPENDENCIES = ["spi"]

# Component declaration only; platform configuration is handled in sensor.py
everblu_ns = cg.esphome_ns.namespace("everblu")
EverbluComponent = everblu_ns.class_("EverbluComponent", cg.PollingComponent)
