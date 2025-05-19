#!/bin/bash
echo "Installing Microk8s Enviroment: this will FORCE a logout; run the install_fishstix.sh again continue the install"
sudo sh fishstix_opt/bin/setup/mk8.sh

if test -f ".mk8s"; then
  echo "Installing pre-requsites for FishStix install_reqs.sh"
  sudo sh fishstix_opt/bin/setup/install_reqs.sh
  echo "Picking up where we left off...running setup_fishstix.sh"
  sleep 1s
  sudo sh fishstix_opt/bin/setup/setup_fishstix.sh
  echo "Finishing setup - please configure Redis"
  sudo sh fishstix_opt/bin/setup/finish_config.sh
else
  echo "Please run the mk8s.sh first"
