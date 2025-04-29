#!/bin/bash
echo "Installing pre-requsites for FishStix install_reqs.sh"
sudo sh bin/setup/install_reqs.sh

if test -f "bin/setup/.placeholder"; then
  echo "Picking up where we left off...setup_fishstix.sh"
  sleep 1s
  sudo sh bin/setup/setup_fishstix.sh
else
  echo "Please run the install_reqs.sh first"
fi

if test -f "/opt/fishstix/yaml/fxcopier.yaml"; then
  echo ""
  sleep 1s
  sudo sh bin/setup/finish_config.sh
else
  echo "Please run the setup_fishstix.sh first"
fi