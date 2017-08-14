#!/bin/bash
#
# PARAMS
# 1 - create or update
#
# READ IN ALL REPOSITORIES
repofile="/repository/storage/repos.config"
read -r repos<$repofile
#
# FOR LOOP FOR ITERATING REPO GENERATION
for mod in $repos
do
repogen.sh $mod $1
done
