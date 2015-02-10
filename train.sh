#!/bin/bash

# Python ENV
export PYTHONPATH=.:$PYTHONPATH

echo "~~~~~ Insert text / comment features into feature table"

python insert_data/build_feature_table.py

echo "~~~~~ Training LDA models"

python prediction/topic_model.py

echo "~~~~~ Insert LDA features into feature table"

python prediction/extended_text_features.py

echo "~~~~~ Training SVMs"

python prediction/prediction_svm.py
