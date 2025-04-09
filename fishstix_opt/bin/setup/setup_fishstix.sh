#!/bin/bash
# Installer Script for Splunk FishStix project
# Kate Lawrence-Gupta - Principal Platform Architect
# https://github.com/splunk/fishstix

#Enable Microk8s DNS & Host-path Storage
echo "Enabling Microk8s: DNS & Host-path Storage"
echo "..."
microk8s enable dns storage 

#create directories needed
echo "Creating directories: /opt/fishstix and moving folders"
echo "..."
sudo mkdir /opt/fishstix
sudo mkdir /opt/fishstix/logs
sudo touch /opt/fishstix/logs/fxcopier.log
sudo touch /opt/fishstix/logs/fxrestore.log

#copy bins/yamls
sudo cp -R fishstix_opt/bin /opt/fishstix/bin
sudo cp -R fishstix_opt/yaml /opt/fishstix/yaml

#patch the bug
sudo cp fishstix/bin/search_command.py /usr/local/lib/python3.10/dist-packages/splunklib/searchcommands/search_command.py

#create Kubernetes namespace called splunk ,configure overall context and set as default
echo "Creating Kubernetes: setting configurations and defaults"
echo "..."
kubectl create ns splunk
kubectl config set-context --current --namespace=splunk
kubectl config view --raw > ~/.kube/config

#apply the yaml files in the following order to create a TCP configmap
echo "Applying YAML configurations:"
echo "..."
echo "Applying YAML - fxcopier x 12 pods""
kubectl apply -f ../yaml/fxcopier.yaml
#Load Balancer for outbound facing TCP/32740 & containers on TCP/8089
echo "Applying YAML - fxrestore x 15 pods"
kubectl apply -f ../yaml/fxrestore.yaml

echo "Applying FishStix SPL app"
/opt/splunk/bin/./splunk install ../fishstix/fishstix.spl

