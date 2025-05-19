#!/bin/bash
# Installer Script for Splunk FishStix project
# Kate Lawrence-Gupta - Principal Platform Architect
# https://github.com/splunk/fishstix

#Requirements
# Splunk 9.4+
# Microk8s 1.32+
# Docker.io
# Redis server, tools & nano
# pip libraries for Redis & Splunk

if
  version=$(sudo /opt/splunk/bin/splunk --version | awk '{print $2}' &&
    [[ -n $version ]] &&
    is-at-least 9.4 $version
then
  echo "FishStix requires the following; Splunk, Docker, Redis-Server/Tools & pip redis and Splunk libraries"
  echo "Installing Docker, Redis and pip"
  sudo apt install nano
  sudo apt install docker.io
  sudo apt install redis-server
  sudo apt install redis-tools
  sudo pip install redis splunklib splunk-sdk
fi
  echo "upgrade Splunk to version 9.4+"


