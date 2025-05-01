#!/bin/bash
# Installer Script for Splunk FishStix project
# Kate Lawrence-Gupta - Principal Platform Architect
# https://github.com/splunk/fishstix

#Requirements
echo "FishStix requires the following; Splunk, Docker, Redis-Server/Tools & pip redis"

if test -f "/opt/splukn/bin"; then
  echo "Splunk is installed."
else
  echo "Please install Splunk first"
fi

#Install the additional required software
echo "Install Docker, Redis server, pip redis"
sudo apt install nano
sudo apt install docker.io
sudo apt install redis-server
sudo apt install redis-tools
sudo pip install redis splunklib splunk-sdk

echo "Running Microk8s installer"