#!/share/bin/python

from optparse import OptionParser
import os
import urllib, json
import re
import sys
import re
import cgi


url="http://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=getFileList"
updateurl="http://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=updateHashBackup&input=%(input)s&dirname=%(dirname)s&hashstr=%(hashstr)s"
def stop_err( msg ):
    sys.stderr.write( "%s\n" % msg )
    sys.exit(2)
   
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
 
def calcHash(amazonbucket, inputfile, ak, sk):
   command="mkdir -p /mnt/tmp; cd /mnt/tmp;"
   command+="s3cmd get --skip-existing --access_key "+ak+" --secret_key "+sk+" "+amazonbucket+"/"+inputfile+">/dev/null;"
   command+="md5sum "+inputfile+" > "+inputfile+".md5sum;"
   print command
   child = os.popen(command)
   jobout = child.read().rstrip()
   err = child.close()
   hashstr = getValfromFile("/mnt/tmp/"+inputfile+".md5sum").split(" ")[0]
   command="rm -rf /mnt/tmp/"+inputfile+"*"
   child = os.popen(command)
   if (len(hashstr) < 10):
       return "" 
   print hashstr
   return hashstr

def getLS(amazonbucket, inputfile):
   command="s3cmd ls "+amazonbucket+"/"+inputfile
   print command
   child = os.popen(command)
   jobout = child.read().rstrip()
   res = False
   if (len(jobout) > 10 ):
      print "\n\nExist:\n"+jobout+"\n\n"
      res = True
   else:
      print "\n\nDoesn't Exist\n\n"
   return res

def runCalcHash(input, dirname, amazon_bucket, ak, sk):
   try:
       files=input.split(',')
       count=0
       hashstr = ""
       if (len(files)>1):
           hashstr1 = ""
           hashstr2 = ""
           if (getLS(amazon_bucket, files[0].strip()) and getLS(amazon_bucket, files[1].strip())):
              hashstr1=calcHash(amazon_bucket, files[0].strip(), ak, sk)
              hashstr2=calcHash(amazon_bucket, files[1].strip(), ak, sk)
           hashstr=hashstr1+","+hashstr2
       else:
           if (getLS(amazon_bucket, input.strip())):
               hashstr=calcHash(amazon_bucket, input.strip(), ak, sk)
       if (len(hashstr)>10):
         input=urllib.quote(input)
         dirname=urllib.quote(dirname)
         urlstr=updateurl%locals()
         print urlstr
         response = urllib.urlopen(urlstr)
   except Exception, ex:
        stop_err('Error (line:%s)running runCalcHash\n%s'%(format(sys.exc_info()[-1].tb_lineno), str(ex)))
  

def main():
   try:
       results=getFileList()
       for result in results:
       
           fastq_dir=result['fastq_dir']
           filename=result['file_name']
           amazon_bucket=result['amazon_bucket']
           ak=result['ak']
           sk=result['sk']
           print fastq_dir 
           print filename 
           print amazon_bucket
           if (amazon_bucket[0:5]=="s3://"):
               runCalcHash(filename, fastq_dir, amazon_bucket, ak, sk) 
   except Exception, ex:
        stop_err('Error (line:%s)running main\n%s'%(format(sys.exc_info()[-1].tb_lineno), str(ex)))

if __name__ == "__main__":
    main()
