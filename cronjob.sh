#!/bin/bash
echo "Starting Colonel Sawyer..."
cd /slackbot/
sudo pkill -F /slackbot/pid.pid
sudo python /slackbot/main.py >> /slackbot/sawyerlog.log 2>&1 &
echo $! > /slackbot/pid.pid
