#!/share/bin/python

from optparse import OptionParser
from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt
import os
import urllib.request
import urllib.parse
import json
import re
import sys
import re
import cgi
import configparser


#url="https://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=getFileList&owner=63"
url="https://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=getFileList"
updateurl="https://dolphin.umassmed.edu/ajax/dolphinfuncs.php?p=updateHashBackup&input=%(input)s&dirname=%(dirname)s&hashstr=%(hashstr)s"
def stop_err( msg ):
    sys.stderr.write( "%s\n" % msg )
    sys.exit(2)
   
def getFileList():
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
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
   command="cd /share/tmp;"
   command+="s3cmd get --skip-existing --access_key "+ak+" --secret_key "+sk+" "+amazonbucket+"/"+inputfile+">/dev/null;"
   command+="md5sum "+inputfile+" > "+inputfile+".md5sum;"
   print(command)
   child = os.popen(command)
   jobout = child.read().rstrip()
   err = child.close()
   hashstr = getValfromFile("/share/tmp/"+inputfile+".md5sum").split(" ")[0]
   command="rm -rf /share/tmp/"+inputfile+"*"
   child = os.popen(command)
   if (len(hashstr) < 10):
       return "" 
   print(hashstr)
   return hashstr

def getLS(amazonbucket, ak, sk, inputfile):
   command="s3cmd ls --access_key "+ak+" --secret_key "+sk+" "+amazonbucket+"/"+inputfile
   print(command)
   child = os.popen(command)
   jobout = child.read().rstrip()
   res = False
   if (len(jobout) > 10 ):
      print("\n\nExist:\n"+jobout+"\n\n")
      res = True
   else:
      print("\n\nDoesn't Exist\n\n")
   return res

def runCalcHash(input, dirname, amazon_bucket, ak, sk):
   try:
       files=input.split(',')
       count=0
       hashstr = ""
       if (len(files)>1):
           hashstr1 = ""
           hashstr2 = ""
           if (getLS(amazon_bucket, ak, sk, files[0].strip()) and getLS(amazon_bucket, ak, sk, files[1].strip())):
              hashstr1=calcHash(amazon_bucket, files[0].strip(), ak, sk)
              hashstr2=calcHash(amazon_bucket, files[1].strip(), ak, sk)
           hashstr=hashstr1+","+hashstr2
       else:
           if (getLS(amazon_bucket, ak, sk, input.strip())):
               hashstr=calcHash(amazon_bucket, input.strip(), ak, sk)
       if (len(hashstr)>10):
         input=urllib.parse.quote(input)
         dirname=urllib.parse.quote(dirname)
         urlstr=updateurl%locals()
         print(urlstr)
         req = urllib.request.Request(urlstr)
         response = urllib.request.urlopen(req)
   except (Exception, ex):
        stop_err('Error (line:%s)running runCalcHash\n%s'%(format(sys.exc_info()[-1].tb_lineno), str(ex)))
  

def main():
   try:
       results=getFileList()
       for result in results:
           config = configparser.ConfigParser()
           config.read(os.path.dirname(os.path.realpath(__file__))+'/.salt')
           password = config.get('Dolphin', 'AMAZON')
           fastq_dir=result['fastq_dir']
           filename=result['file_name']
           amazon_bucket=result['amazon_bucket']
           ak=decrypt(password, unhexlify(result['ak']))
           sk=decrypt(password, unhexlify(result['sk']))
           print(fastq_dir)
           print(filename)
           print(amazon_bucket)
           if (amazon_bucket[0:5]=="s3://"):
               runCalcHash(filename, fastq_dir, amazon_bucket, ak, sk) 
   except (Exception, ex):
        stop_err('Error (line:%s)running main\n%s'%(format(sys.exc_info()[-1].tb_lineno), str(ex)))

if __name__ == "__main__":
    main()
