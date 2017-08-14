#!/bin/bash
#
# PARAMS TO BE PASSED
# 1 - repo name
# 2 - create or update
#
#stop repository server from operating
service apache2 stop
#
#read in swifty generation parameters and pass repo name to folder
paramfile="/repository/storage/$1""ignore"
read -r params<$paramfile
#
#wipe repository folder
if [ "$2" == "create" ]; then rm -rf /var/www/html/$1; fi
#
#prepare blank repository settings for generation
cd /repository/input
if test -f "repo.config"; then rm repo.config; fi
if test -f "repo.png"; then rm repo.png; fi
#
#prepare dev repository for generation
cp "/repository/storage/$1""repo.config" repo.config
cp "/repository/storage/$1""repo.png" repo.png
#
#generate repository
cd /repository/tools
mono swifty-cli.exe $2 ../input /var/www/html/$1 -ignore "$params"
#
#prepare blank repository settings for generation
cd /repository/input
if test -f "repo.config"; then rm repo.config; fi
if test -f "repo.png"; then rm repo.png; fi
#
#restart repository server
service apache2 start