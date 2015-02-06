#!/bin/bash

# ~~~~~ STEP 0: SETUP
# Create directories
mkdir output
cd output
mkdir stackoverflow-data
cd stackoverlow-data

# Python ENV
export PYTHONPATH=.:$PYTHONPATH

# ~~~~~ STEP 1: DOWNLOAD DATA

# Places the stackoverflow dump into the data folder. The latest data dump
# can be downloaded using torrent from https://archive.org/details/stackexchange
# we will try it using wget
wget https://archive.org/download/stackexchange/stackoverflow.com-Badges.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Comments.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-PostHistory.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-PostLinks.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Users.7z
wget https://archive.org/download/stackexchange/stackoverflow.com-Votes.7z

# ~~~~~ STEP 2: UNZIP THE SO DATA DUMP
for arc in *.7z
do
  7za e "$arc"
done

cd ../..

# ~~~~~ STEP 3: CONVERT DATA XML -> SQL
python runner/convert_data.py
