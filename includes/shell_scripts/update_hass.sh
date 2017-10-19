#!/bin/bash -x

##########################################
## This script upgrades the OS          ##
## upgrades HA then reboots             ##
##########################################

# https://community.home-assistant.io/t/script-that-stops-hass-updates-hass-and-starts-hass-again/3330/21
#sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove
hassctl update-hass && hassctl config && hassctl restart

# This requires a modification using `sudo visudo`:
#   https://community.home-assistant.io/t/lets-encrypt-installation-need-help/28468/4

