#!/bin/bash

# This is the installer required to be run to ensure all
# necessary dependencies are installed.
# This installer will NOT install:
#   - java > 1.7
#   - python > 2.6
#   - easy_install for python
#   - SQL server
# Those dependencies should be pre-installed.

# SUSE Installer

# Natural language processing package
sudo easy_install nltk

# Version must be >= 1.4 to work for `gensim
# Numpy needs the fortran compiler
sudo zypper install gcc-fortran
sudo zypper install python-numpy

# Helper to run SVM training in reasonable amount of time
# On the crawler server that resulted in problems when installing 
# `numpy`, therfore install lapack after `numpy`
sudo zypper install liblapack3

sudo zypper install python-scipy

# LDA Topic models for python
sudo easy_install gensim

# SVMs for python
sudo easy_install scikit-learn

# Simple webserver for python
sudo easy_install flask
sudo easy_install requests
