#!/usr/bin/env python
#

""" ipinfo.py

Base support for rim things.

"""
import sys
import logging
import subprocess
from selector import *
from logging.handlers import *

class Rim():

    def getCmdLine(self, field):
        if field in self.cmdFields: return self.cmdFields[field]
        return "NotFound"

    def curVersion(self):
        return self.getCmdLine("version")

    def curNode(self):
        return self.getCmdLine("rim_node")

    def curVariant(self):
        return self.getCmdLine("rim_variant")
        
    def curVersionRoot(self):
        return self.versionRoot(self.curVersion)

    def versionRoot(version):
        return "%s/%s" % (self.softDir, version)
        
    def __init__(self):
    
        # initialize the cmdline fields
        try:
            cmdline=open("/proc/cmdline", "r").read()
        except:
            print "Failed to access /proc/cmdline"
            sys.exit(1)
            
        fields=cmdline.split()
        self.cmdFields={}
        for field in fields:
            tokens=field.split("=")
            if len(tokens) > 1:
                self.cmdFields[tokens[0]]=tokens[1]
            
        # some constants
        self.softDir="/soft"
        self.dataDir="/data"
        
        # version

syslog=None
    
class logger():
    
    def __init__(self, name, debug=False):
        
        global syslog
        self.name=name
        self.ok=True
        self.debug=debug
        if syslog is not None:
            #logger has already been initialized
            self.syslog = syslog
            return
        syslog=logging.getLogger(name)
        self.syslog = syslog
        self.syslog.setLevel(logging.DEBUG)
        try:
            self.syslog.addHandler(logging.handlers.SysLogHandler(address = '/dev/log'))
            self.ok=True
        except:
            self.ok=False
        
    def log(self, s):
        if self.ok: 
            if self.debug:
                sys.stderr.write("[ %s ] %s\n" %(self.name, s))
            else:
                self.syslog.debug("[ %s ] %s" %(self.name, s))

def logLines(logger, prefix, txt):
    lines=txt.split("\n")
    for line in lines:
        if len(line):
            logger("[%s] %s\n" % (prefix, line))

####################################################
# convert Json to object
class Object(object):
    pass

def jsonToObject(json):
        o=Object()
        for key in json:
            if isinstance(json[key], dict):
                setattr(o, key, jsonToObject(json[key]))
            elif isinstance(json[key], list):
                l=[ jsonToObject(json[key][idx]) for idx in range(0, len(json[key])) ]
                setattr(o, key, l)
            else:
                setattr(o, key, json[key])
        return o
#
####################################################

import fcntl
def unBlock(fd):
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    return fd

class childHandler():

    def __init__(self, log, child):
        self.stdout=child.stdout
        self.stderr=child.stderr
        self.out=unBlock(child.stdout.fileno())
        self.err=unBlock(child.stderr.fileno())
        self.outbuf=""
        self.errbuf=""
        self.log=log
        
    def chkHandles(self, rlist, wlist, xlist):
        if self.out in  rlist:
            s=self.stdout.read()
            if len(s) == 0: return False
            self.outbuf=self.outbuf+s
            
        if self.err in rlist:
            s=self.stderr.read()
            if len(s) == 0: return False
            self.errbuf=self.errbuf+s
            
        return True
    
    def releaseHandles(self):
        return
    
    def initHandles(self):
        return
    
    def setHandles(self, rlist, wlist, xlist):
        rlist.append(self.out)
        rlist.append(self.err)

def runCmd(logger, cmd, exitOk=[0], errors=None, out=None):
    logger("cmd='%s'" % (cmd))
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    sel=selector()
    handler=childHandler(logger, child)
    sel.addHandler(handler)
    sel.waitLoop()
    logLines(logger, "error", handler.errbuf)
    logLines(logger, "stdout", handler.outbuf)
    ret = child.wait()
    if out != None:
        for msg in handler.outbuf.split("\n"):
            out.append(msg)
        if not len(out[0]):
            out[0]="Unknown"
    if errors != None:
        for err in handler.errbuf.split("\n"):
            if len(err) : errors.append(err)
        if len(errors) and not len(errors[0]):
            errors[0]="Unknown"
    if ret not in exitOk:
        logger("Failed with %d" % ret)
        return False, ret
    return True, ret

#
# general class to setup a selectable handle for file change
#
import signal
class fileMon():

    def __init__(self, log, fileName):
        self.s=None
        self.log=log
        self.fileName=fileName

    def initHandles(self):
        self.child = subprocess.Popen([ '/usr/bin/inotifywait','-m','-e','modify', self.fileName ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # flush the initial 2 line output
        # Setting up watches. 
        # Watches established.
        self.child.stderr.readline()
        self.child.stderr.readline()
        self.s=self.child.stdout
        self.log("Watcher handle is %d for file %s" % (self.s.fileno(), self.fileName))
        
    def chkHandles(self, rlist, wlist, xlist):
        if self.s and self.s.fileno() in rlist:
            self.log("File %s changed" % self.fileName)
            self.s.readline()
            return False
        return True
                
    def setHandles(self, rlist, wlist, xlist):
        if self.s:
            rlist.append(self.s.fileno())
        
    def releaseHandles(self):
        if self.s:
            os.kill(self.child.pid, signal.SIGKILL)
            del self.child
            self.s.close()
            self.s=None
