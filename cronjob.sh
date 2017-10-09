#!/bin/bash
echo "Starting Colonel Sawyer..."
sudo pkill -F /python/slackbot/pid.pid
sudo python /python/slackbot/main.py &
echo $! > /python/slackbot/pid.pid
