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

#Modify the redis.conf file
echo "Redis-Server needs to be configured locally"
echo "please open the /etc/redis/redis.conf and set the bind address to the local IP of this host and change protected mode from yes to no"
sleep 5s
echo "restart Redis service"
service redis-server status

echo "This will install Microk8s version 1.32, setup current user for kubes and create the alias for kubectl"
sudo snap install microk8s --classic --channel=1.32/stable
sudo usermod -a -G microk8s splunker
sudo chown -f -R splunker ~/.kube
sudo snap alias microk8s.kubectl kubectl
touch .placeholder
echo "logout now and back in to continue setup with setup_fishstix.sh"
