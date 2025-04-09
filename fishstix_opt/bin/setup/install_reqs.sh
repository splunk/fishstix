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
apt install docker.io
apt install redis-server
apt install redis-tools
pip install redis splunklib

echo "This will install Microk8s version 1.32, setup current user for kubes and create the alias for kubectl"
sudo snap install microk8s --classic --channel=1.32/stable
sudo usermod -a -G microk8s splunker
sudo chown -f -R splunker ~/.kube
sudo snap alias microk8s.kubectl kubectl
echo "logout now and back in to continue setup with setup_fishstix.sh""
