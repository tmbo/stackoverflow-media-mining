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

# 7zip is needed to unpack the stackoverflow data
sudo zypper install p7zip

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
sudo easy_install ordereddict

echo "Next steps to do MANUALLY:"
echo "Download SAP HANA driver from"
echo "https://downloads.sdn.sap.com/hana/hana10/sap_hana_client_linux64.tgz"
echo "Follow instructions on how to setup python with HANA http://scn.sap.com/community/developer-center/hana/blog/2014/05/02/connect-to-sap-hana-in-python"

read -p "Are you finished? (Y|y)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  # Installation of sbt for scala
  wget https://repo.typesafe.com/typesafe/ivy-releases/org.scala-sbt/sbt-launch/0.13.7/sbt-launch.jar -P sbt/
  cd sbt
  printf '
  SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled -XX:MaxPermSize=256M"
  java $SBT_OPTS -jar `dirname $0`/sbt-launch.jar "$@"\n' >> sbt
  chmod +x sbt
  cd ..
else
  echo "Aborting"
  exit 1



