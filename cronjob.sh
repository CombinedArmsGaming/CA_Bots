#!/bin/bash
echo "Starting Colonel Sawyer..."
cd /slackbot/
pkill -F /slackbot/pid.pid
python3 /slackbot/main.py >> /slackbot/sawyerlog.log 2>&1 &
echo $! > /slackbot/pid.pid
