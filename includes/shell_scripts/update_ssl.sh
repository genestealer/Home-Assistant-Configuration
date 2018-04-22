#!/bin/bash
# This is for log purposes
echo "[$(date)] Renew SSL cert script starting"
echo "Current path $PWD"
/home/thor/certbot/certbot-auto renew --no-self-upgrade --standalone --preferred-challenges http-01 --post-hook "hassctl restart" #--pre-hook "hassctl stop"
