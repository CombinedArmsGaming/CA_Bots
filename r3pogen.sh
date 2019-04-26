#!/bin/bash
#
# PARAMS TO BE PASSED 1 - repo name
#
#stop repository server from operating
#service apache2 stop
#
#read in swifty generation parameters and pass repo name to folder
paramfile="/repository/storage/$1""repo.json"
#
#wipe repository folder
rm -rf /repository/www/$1
#
#prepare blank repository settings for generation
cd /repository/input
if test -f "repo.png"; then rm repo.png; fi
#
#prepare dev repository for generation
cp "/repository/storage/$1""repo.png" repo.png
#
#generate repository
cd /repository/tools
mono newcli.exe create $paramfile /repository/www/$1 --nocopy
#
find /repository/www/$1/* -maxdepth 1 -type d -print0 |
  while IFS= read -rd '' dir; do echo "$dir"; dir2=${dir%*/}; dir3=${dir2##*/}; echo $dir3; cp "/repository/input/$dir3""/" "/repository/www/$1""/" -as; done
#
#prepare blank repository settings for generation
cd /repository/input
if test -f "repo.png"; then rm repo.png; fi
#
#restart repository server
#service apache2 start
