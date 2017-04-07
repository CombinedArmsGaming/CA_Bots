#!/bin/bash

#A short script to retrieve the pid and kill the bots in the event of a manual service halt being necessary.

echo "Killing Colonel Sawyer..."
sudo pkill -F /python/slackbot/pid.pid
