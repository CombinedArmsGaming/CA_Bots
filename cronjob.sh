#!/bin/bash

#This script runs as a cronjob on the server to kill and restart the bot once a day.

echo "Starting Colonel Sawyer..."
sudo pkill -F /python/slackbot/pid.pid
sudo python /python/slackbot/ops_control.py &
echo $! > /python/slackbot/pid.pid
