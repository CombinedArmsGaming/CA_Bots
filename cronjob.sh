#!/bin/bash
echo "Starting Colonel Sawyer..."
sudo pkill -F /python/slackbot/pid.pid
sudo python /python/slackbot/main.py >> /python/slackbot/sawyerlog.log 2>&1 &
echo $! > /python/slackbot/pid.pid