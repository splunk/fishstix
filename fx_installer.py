#KLG FishStix installer

import os
import configparser
import time
import sys



def install_mk8s(mk8_version,user):
    cmd_install = str("sudo snap install microk8s --classic --channel="+mk8_version)
    cmd_user_mod = str("sudo usermod -a -G microk8s "+user)
    cmd_chown_mod = str("sudo chown -f -R "+user+" ~/.kube ")
    cmd_set_kubectl = str("sudo snap alias microk8s.kubectl kubectl")
    placeholder = str("sudo touch .placeholder")
    os.system(cmd_install)
    os.system(cmd_user_mod)
    os.system(cmd_chown_mod)
    os.system(cmd_set_kubectl)
    os.system(placeholder)
    print("Installation of Microk8s is complete; please logout and back in to resume installation")

def splunk_check():
    cmd_splunk_version = str("sudo /opt/splunk/bin/splunk version")
    splunk_version = str(os.system(cmd_splunk_version))
    return splunk_version

def configure_redis_server(ip_address):
    print("Nano will open the /etc/redis/redis.conf file for editing: plesae set the bind addresss to the IP of this host:"+ip_address+"and protected mode to NO")
    time.sleep(2)
    config_redis_server = str("sudo nano /etc/redis/redis.conf")
    os.system(config_redis_server)
    restart_redis = str("sudo service redis restart")
    os.system(restart_redis)


def install_reqs():
    apt_install_list = str("sudo apt -qq install nano docker.io redis-server redis-tools")
    pip_install_list = str("sudo pip install redis splunklib splunk-sdk")
    os.system(apt_install_list)
    os.system(pip_install_list)

def check_mk8s():
    os.system("sudo microk8s status")

def enable_mk8s():
    os.system("sudo microk8s enable dns storage")

def configure_k8s():
    k8_create_ns = str("sudo kubectl create ns splunk")
    k8_set_context = str("sudo kubectl config set-context --current --namespace=splunk")
    k8_config_view = str("sudo kubectl config view --raw > ~/.kube/config")
    os.system(k8_create_ns)
    os.system(k8_set_context)
    os.system(k8_config_view)

def configure_fishstix(user):
    fx_mkdir = str("sudo mkdir /opt/fishstix")
    fx_mkdir_logs = str("sudo mkdir /opt/fishstix/logs")
    fx_copy_log = str("sudo touch /opt/fishstix/logs/fxcopier.log")
    fx_restore_log = str("sudo touch /opt/fishstix/logs/fxrestore.log")
    fx_copy_log = str("sudo cp -R /home/"+user+"/fishstix/fishstix_opt/bin /opt/fishstix/")
    fx_restore_log = str("sudo cp -R /home/"+user+"/fishstix/fishstix_opt/yaml /opt/fishstix/")
    os.system(fx_mkdir)
    os.system(fx_mkdir_logs)
    os.system(fx_copy_log)
    os.system(fx_restore_log)



def configure_fxcopier_redis(ip_address):
    fxcopier_conf = "/opt/fishstix/bin/fxcopier/fxcopier.conf"
    config = configparser.ConfigParser()
    config.read(fxcopier_conf)
    section_name = 'config'
    key_name = 'redis_host'
    new_value = str(ip_address)
    config.set(section_name, key_name, new_value)
    with open(fxcopier_conf, 'w') as configfile:
        config.write(configfile)


def configure_fxrestore_redis(ip_address):
    fxrestore = "/opt/fishstix/bin/fxrestore/fxrestore.conf"
    config = configparser.ConfigParser()
    config.read(fxrestore)
    section_name = 'config'
    key_name = 'redis_host'
    new_value = str(ip_address)
    config.set(section_name, key_name, new_value)
    with open(fxrestore, 'w') as configfile:
        config.write(configfile)


def configure_spledis(ip_address):
    fxrestore = "/opt/splunk/etc/apps/fishstix/default/spledis.conf"
    config = configparser.ConfigParser()
    config.read(fxrestore)
    section_name = 'config'
    key_name = 'host'
    new_value = str(ip_address)
    config.set(section_name, key_name, new_value)
    with open(fxrestore, 'w') as configfile:
        config.write(configfile)




def configure_splunk(user,ip_address):
    patch_bug = str("sudo cp /home/"+user+"/fishstix/fishstix_opt/bin/setup/search_command.py /usr/local/lib/python3.10/dist-packages/splunklib/searchcommands/search_command.py")
    install_fx_app = str("sudo /opt/splunk/bin/./splunk install app /home/"+user+"/fishstix/fishstix.spl")
    restart_splunk = str("sudo /opt/splunk/bin/./splunk restart")
    os.system(patch_bug)
    os.system(install_fx_app)
    os.system(restart_splunk)
        
if __name__ == "__main__":
    mk8_version=str("1.32/stable")
    user = str("splunker")
    host = str(os.system("sudo hostname"))
    ip_address = str(sys.argv[1])
    placeholder = ".placeholder"  
    if os.path.exists(placeholder):
       enable_mk8s()
       configure_k8s()
       install_reqs()
       configure_fishstix(user)       
       configure_redis_server(ip_address)
       configure_fxcopier_redis(ip_address)    
       configure_fxrestore_redis(ip_address)
       configure_splunk(user,ip_address)
       configure_spledis(ip_address)
    else:
       install_mk8s(mk8_version,user)
 
  