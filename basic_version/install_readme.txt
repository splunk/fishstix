Install instructions for a FishStix Inventory node


Packages required:
- nfs-common/focal-updates,now 1:1.3.4-2.5ubuntu3.7 amd64 [installed]
- sshfs/focal,now 3.6.0+repack+really2.10-0ubuntu1 amd64 [installed]
- openjdk-21-jre/focal-updates,focal-security,now 21.0.2+13-1~20.04.1 amd64 [installed]
- unzip/focal-updates,now 6.0-25ubuntu1.2 amd64 [installed]

Splunk Universal Forwarder Setup
wget splunkforwarder-9.2.1-78803f08aabb-Linux-x86_64.tgz
download & deploy the following configurations to etc/system/local
- inputs.conf
	[tcp://127.0.0.1:9995]
	queueSize = 2GB
	persistentQueueSize = 50GB
	sourcetype=fs_inventory_data
	source = tcp:9995
	index = fs_inventory
- outputs.conf //to the Splunk FishStix UI node configured with the fs_inventory index
	[tcpout:fs_standalone]
	server=x.x.x.x:9997
- props.conf
	[fs_inventory_data]
	EVENT_BREAKER_ENABLE = true
	EVENT_BREAKER = "([\r\n]+)"

Mount Points
- create mount points for NFS & SSHFS at /mnt/nfs  & /mnt/sshfs respectively 
	- mount the NFS share you want to poll /mnt/nfs; each Splunk index should be in it's own directory
	- mount the SSHFS share you want to poll /mnt/sshfs; each Splunk index should be in it's own directory

NIFI Setup
- wget https://dlcdn.apache.org/nifi/1.26.0/nifi-1.26.0-bin.zip
- grep log for Generated to get Username/Password info
- Manual: Upload xml template & add template to NIFI workspace >> start processors