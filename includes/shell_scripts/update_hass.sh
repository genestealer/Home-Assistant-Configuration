#!/bin/bash

# This is for log purposes
echo
echo "[$(date)] Update script starting"

# https://github.com/dale3h/hassctl
# Update HA, run the config checker and only if it passes then restart HA.
# This requires a modification using `sudo visudo`:
# E.G. "homeassistant ALL=(ALL) NOPASSWD:SETENV: /bin/systemctl"

hassctl update-hass && hassctl config && hassctl restart




##########################################
## This script upgrades the OS          ##
## upgrades HA then reboots             ##
##########################################

# https://community.home-assistant.io/t/script-that-stops-hass-updates-hass-and-starts-hass-again/3330/21
#sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove

# This requires a modification using `sudo visudo` to include "/bin/systemctl"
# E.G. homeassistant ALL=(ALL) NOPASSWD:SETENV: /bin/systemctl
#   https://community.home-assistant.io/t/lets-encrypt-installation-need-help/28468/4

