## Fishstix - a Splunk frozen data management tool

Splunk can create frozen indexed data in a compressed format (journal.gz) to reduce storage costs, but there are a few downsides:

 - frozen data is not searchable w/o it's metadata being restored
 - frozen data is not organized in the drop off location and can be
   difficult to manage
 - by default Splunk restore operations run serially (one-after-another)
   which can take a long time to process.

Fishstix attempts to resolve these known issues by using a standalone Splunk host to : 

 -  runs NIFI to create a live inventory of Splunk frozen data from a mounted
    location 
	 - (NFS, SSHFS, S3FS supported) in Splunk (index=fx).
	 - This inventory gives the original time ranges and index of the
    buckets so we can filter out the specific buckets to restore.
 - the FishStix lookup builder dashboard (xml) is provided to help build a lookup file (restorequeue.csv) from the (NIFI-provided) inventory of the buckets you want to restore
 - Use the provided fishstix.sh file to either:

1. Start Copy to index _*must be run prior to Restore - data cannot be rebuild without being staged_
2. Start Restore to index
3. View Kubernetes Status
4. Clear restorequeue.csv lookup file

FishStix restore process
 - uses custom REDIS queue to create a list of buckets to be processed
 - Data is restored to the restored_data_100 by default

 - the "Start Copy to index" process is run by the fxcopier.yaml containers (2 replicas by default)
	 - these containers will read from the REDIS **copyqueue** and copy the buckets identified from
   the **restorequeue.csv** file to the staged index located at
   **/mnt/data/restored_data_100**
	 - Progress is logged at /mnt/data/fxcopier.log
 - the "Start Restore to index" process is run by fxrestore.yaml containers (5 replicas by default)
	 - these containers read from the REDIS **restorequeue** and begin the thawing/rebuild process in the **restore_data_100** index
	 - This can be scaled up to 5 replicas on an m5.4xlarge instance for
   maximum performance
    - Progress is logged at /mnt/data/fxrestore.log


