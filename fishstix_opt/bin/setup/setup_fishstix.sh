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
sudo cp -R /home/splunker/fishstix_opt/ /opt/fishstix/


#patch the bug
sudo cp /home/splunker/fishstix_opt/bin/search_command.py /usr/local/lib/python3.10/dist-packages/splunklib/searchcommands/search_command.py

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
kubectl apply -f /opt/fishstix/yaml/fxcopier.yaml
echo "Applying YAML - fxrestore x 5 pods"
kubectl apply -f /opt/fishstix/yaml/fxrestore.yaml

echo "Applying FishStix SPL app"
/opt/splunk/bin/./splunk install /home/splunker/fishstix/fishstix.spl

