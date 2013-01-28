import time
import xmlrpclib

# Connect to the HQueue server.
hq_server = xmlrpclib.ServerProxy( "http://hqueue:5000")

# Make sure the server is running.
try:
         hq_server.ping()
except:
         print "HQueue server is down."


# Define a job which renders an image from an IFD using Mantra.
job_name = "Weekly Render"
ifd_path = "$JOB/" #TODO set by user
output_path = "$JOB/" #TODO set by user
frames_to_render = [1,2,3] #TODO set by user

# generate frame-specific jobs
children = []
for frame in frames_to_render:
		child = { 
                        "name":	"Render Frame " + frame,
                        "shell":	"bash",
                        "command": 
                        "cd $HQROOT/houdini_distros/hfs; 
                        source houdini_setup; 
                        cd "+ifd_path+"
                        mantra < " + ifd_path + "frame0" + frame +".ifd"
               }
		children.append(child)

job_spec = 
{ 
         "name":	job_name,
         "shell":	"bash",
         "command": 
                  "cd $HQROOT/houdini_distros/hfs"
                  + "source houdini_setup"
                  + "cd " + output_path +";"
						+ "for F in " + ifd_path + "*.ifd"
						+ "do"
						+ "echo Doing ifd: $F"
						+ "mantra -f $F"
						+ "echo Finished ifd: $F"
						+ "done"
         "children": children
}

# Submit the job to the server.
# newjob() returns a list of job ids (in case multiple jobs are passed in at once).
job_ids = hq_server.newjob(job_spec)

# Periodically check the job progress and status.
while True:
         # Get the job status. 
         job_details = hq_server.getJob(job_ids[0], [ "progress", "status"])
         status = job_details["status"] 

         # Check if the job is finished. 
         if status in ("succeeded", "failed", "cancelled", "abandoned"):
                  break

         # Job is not finished. Output its progress. 
         progress = job_details["progress"]          print "Progress: %.2f" % (progress * 100) 

# Output final status. 
print "Status: ", job_details["status"]