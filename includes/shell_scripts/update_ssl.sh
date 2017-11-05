#!/bin/bash
# This is for log purposes
echo
echo "[$(date)] Renew SSL cert script starting"
/certbot/certbot-auto renew --quiet --no-self-upgrade --standalone --preferred-challenges http-01 #--pre-hook "hassctl stop" --post-hook "hassctl start"