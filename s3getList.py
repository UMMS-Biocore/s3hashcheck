#!/share/bin/python

from optparse import OptionParser
import os
import urllib, json
import re
import sys
import re
import cgi

url="http://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=getFileList"
   
def getFileList():

    response = urllib.urlopen(url);
    data = json.loads(response.read())

    return data

def getValfromFile(filename):
    val=''
    if (os.path.isfile(filename)):
    	infile = open(filename)
    	val = infile.readlines()[0].rstrip()
    else:
    	sys.exit(84)
    return val
 
def getList(amazonbucket, inputfile):
   command="s3cmd ls "+amazonbucket+"/"+inputfile
   print command
   child = os.popen(command)
   jobout = child.read().rstrip()
   return jobout 


def runGetList(input, dirname, amazon_bucket):
   files=input.split(',')
   count=0
   if (len(files)>1):
     file1=getList(amazon_bucket, files[0].strip())
     file2=getList(amazon_bucket, files[1].strip())
     file="["+file1+"],["+file2+"]"
   else:
     file=getList(amazon_bucket, input.strip())

   if (len(file) > 10 ):
      print "\n\nExist:\n"+file+"\n\n"
   else:
      print "\n\nDon't Exist\n\n"

def main():

   results=getFileList()
   for result in results:
       
       fastq_dir=result['fastq_dir']
       filename=result['file_name']
       amazon_bucket=result['amazon_bucket']
       print fastq_dir 
       print filename 
       print amazon_bucket
       runGetList(filename, fastq_dir, amazon_bucket)

if __name__ == "__main__":
    main()
