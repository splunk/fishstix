## Fishstix - a Splunk frozen data management tool

Splunk can create frozen indexed data in a compressed format (journal.gz) to reduce storage costs, but there are a few downsides:

 - frozen data is not searchable w/o it's metadata being restored
 - frozen data is not organized in the drop off location and can be
   difficult to manage
 - by default Splunk restore operations run serially (one-after-another)
   which can take a long time to process.

Fishstix attempts to resolve these known issues by using a standalone Splunk host to : 

 - use NIFI to create an inventory of Splunk frozen data from a mounted
    location 
	 - (NFS, SSHFS, S3FS supported) in Splunk (index=fx).
	 - This inventory gives the original time ranges and index of the
    buckets so we can filter out the specific buckets to restore.
 - Determine which buckets you want from the inventory and put that
    list in a lookup called **restorequeue.csv**
 - Run the buildqueue.py script to load the **restorequeue.csv** file into the REDIS
    queue for copy & restore processing.

FishStix restore process
 - uses REDIS to create a queue of work to be processed
 - Data is restored to the restored_data_100 by default

 - the COPY is run by the fxcopier.yaml containers (2 replicas by default)
	 - will read from the REDIS **copyqueue** and copy the buckets identified from
   the **restorequeue.csv** file to the staged index located at
   **/mnt/data/restored_data_100**
	 - Progress is logged at /mnt/data/fxcopier.log
 - the RESTORE fxrestore.yaml (1 replica by default)
	 -  read from the REDIS **restorequeue** and begin the thawing/rebuild process in the **restore_data_100** index
	 - This can be scaled up to 5 replicas on an m5.4xlarge instance for
   maximum performance
    - Progress is logged at /mnt/data/fxrestore.log


