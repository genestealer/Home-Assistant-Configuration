# #!/bin/sh
# echo
# echo "Home Assistant update script for Hassbian"
# echo 

# echo "Stopping Home Assistant Service"
# sudo systemctl stop home-assistant@homeassistant.service

# echo "Changing to the homeassistant user"
# sudo -u homeassistant -H /bin/bash << EOF

# echo "Changing to Home Assistant venv"
# source /srv/homeassistant/bin/activate

# echo " Update to latest version of Home Assistant"
# pip3 install --upgrade homeassistant

# echo "Deactivating virtualenv"
# deactivate
# EOF

# echo "Changing to the pi user"
# sudo -u pi -H /bin/bash << EOF

# echo "Starting Home Assistant Service"
# sudo systemctl start home-assistant@homeassistant.service