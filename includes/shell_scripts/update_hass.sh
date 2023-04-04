h#!/bin/bash

# This is for log purposes
echo
echo "[$(date)] HA update script starting, using HASSCTL"

# https://github.com/dale3h/hassctl
# USeing HASSCTL this script updates HA, runs the config checker and only if it passes  restart HA.
# This requires a modification using `sudo visudo`:E.G. "homeassistant ALL=(ALL) NOPASSWD:SETENV: /bin/systemctl"
# A log of this script is stored in the same location as this script.
# Example of HA shell_command used to call this script: update_and_restart_hass_with_logging: "/bin/bash /home/homeassistant/.homeassistant/includes/shell_scripts/update_hass.sh </dev/null >> /home/homeassistant/.homeassistant/includes/shell_scripts/update_hass.log 2>&1 &"
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

