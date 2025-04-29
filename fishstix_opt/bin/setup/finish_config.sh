#!/bin/bash
# Installer Script for Splunk FishStix project
# Kate Lawrence-Gupta - Principal Platform Architect
# https://github.com/splunk/fishstix


Modify the redis.conf file
echo "Redis-Server needs to be configured locally"
echo "Opening /etc/redis/redis.conf for editing"
echo "add a bind address for this host IP and set protected mode to no"
sleep 2s
nano /etc/redis/redis.conf
sleep 1s
echo "Opening /opt/fishstix/bin/fxrestore/fxrestore.conf for editing"
echo "set the redis_host to the host IP"
nano /opt/fishstix/bin/fxrestore/fxrestore.conf
sleep 1s
echo "Opening /opt/fishstix/bin/fxcopier/fxcopier.conf for editing"
echo "set the redis_host to the host IP"
nano /opt/fishstix/bin/fxcopier/fxcopier.conf

echo "restart Redis service"
service redis-server status

#apply the yaml files in the following order to create a TCP configmap
echo "Creating Pods:"
echo "..."
echo "..."

echo "Applying FXCopier YAML - fxcopier x 12 pods"
sudo kubectl apply -f /opt/fishstix/yaml/fxcopier.yaml
echo "..."

echo "Applying FXRestore YAML - fxrestore x 5 pods"
sudo kubectl apply -f /opt/fishstix/yaml/fxrestore.yaml
echo "..."

