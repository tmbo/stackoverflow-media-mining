#!/bin/bash

echo "~~~~~ STEP 0: SETUP"
# Create directories
mkdir output
cd output
mkdir stackoverflow-data
cd stackoverlow-data

# Python ENV
export PYTHONPATH=.:$PYTHONPATH

echo "~~~~~ STEP 1: DOWNLOAD DATA"

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

echo "~~~~~ STEP 2: UNZIP THE SO DATA DUMP"
for arc in *.7z
do
  7za e "$arc" -aoa
done

rm -rf *.7z
cd ../..

echo "~~~~~ STEP 3: INSERT DATA INTO HANA"
python insert_data/insert_data.py

echo "~~~~~ STEP 4: CREATE ADDITIONAL TAG TABLES"
python prediction/tag_aggregation_features.py