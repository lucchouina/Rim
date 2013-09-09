
import sys
import os
import hashlib
from string import Template

def translate(str, dic=os.environ):
    return Template(str).substitute(dic);

def fileDigest(fname, blksize):
    file=open(fname, 'r')
    mymd5=hashlib.md5()
    s=file.read(blksize)
    while len(s) > 0:
        mymd5.update(s)
        s=file.read(blksize)
    return mymd5.hexdigest()
