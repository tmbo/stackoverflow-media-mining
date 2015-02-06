#!/bin/bash

# 1. Place the stackoverflow dump into the data folder. The latest data dump
# can be downloaded using torrent from https://archive.org/details/stackexchange
# we will try it using wget

# Create directories
mkdir output
cd output
mkdir stackoverflow-data
cd stackoverlow-data

wget https://archive.org/download/stackexchange/stackoverflow.com-Badges.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Comments.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-PostHistory.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-PostLinks.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Users.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Votes.7z

export PYTHONPATH=.:$PYTHONPATH

# Let's unzip the stackoverflow data
for arc in *.7z
do
  7za e "$arc"
done

cd ../..

# convert the stackoverflow data from xml files to sql files
python runner/convert_data.py
