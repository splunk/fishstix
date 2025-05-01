!#/bin/bash
echo "This will install Microk8s version 1.32, setup current user for kubes and create the alias for kubectl"
sudo snap install microk8s --classic --channel=1.32/stable
sudo usermod -a -G microk8s splunker
sudo chown -f -R splunker ~/.kube
sudo snap alias microk8s.kubectl kubectl
touch .placeholder
echo "logout now and back in to continue setup with setup_fishstix.sh"