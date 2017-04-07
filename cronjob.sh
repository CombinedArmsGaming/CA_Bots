#!/bin/bash
echo "Starting Colonel Sawyer..."
sudo pkill -F /python/slackbot/pid.pid
sudo python /python/slackbot/ops_control.py &
echo $! > /python/slackbot/pid.pid
