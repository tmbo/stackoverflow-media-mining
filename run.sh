#!/bin/bash

# 1. Place the stackoverflow dump into the data folder. The latest data dump
# can be downloaded using torrent from https://archive.org/details/stackexchange
export PYTHONPATH=.:$PYTHONPATH

# Let's unzip the stackoverflow data
cd output/stackoverflow-data
for arc in *.7z
do
  7za e "$arc"
done
cd ../..

# convert the stackoverflow data from xml files to sql files
python runner/convert_data.py
