import sys
import os
import hashlib
import inspect
from string import Template
import xml.dom.minidom
try:
    from SCons import Environment
except:
    pass
import string
'''

TODO: add line numbers to print output?

  import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

'''

class Rimcore:

    def fileDigest(self, fname, blksize):
        file=open(fname, 'r')
        mymd5=hashlib.md5()
        s=file.read(blksize)
        while len(s) > 0:
            mymd5.update(s)
            s=file.read(blksize)
        return mymd5.hexdigest()

    def dbg(self, level, fmt, *args):
        if level <= self.dbglvl:
            print fmt % args 
            if self.showLine:
                self.bt(s)

    def bt(self, count=10):
        s=""
        frame=inspect.currentframe().f_back
        for i in range(1,count):
            if not frame:
                break
            s+="    %s %d\n" % (frame.f_code.co_filename, frame.f_lineno)
            frame = frame.f_back
        print s

    def dbglevel(self, level, show=False):
        self.dbglvl=level
        self.showLine=0
        
    def __init__(self):
        self.dbglvl=0
        self.showLine=False
        #self.dbgLibName="libhistory.so.5"
        self.dbgLibName=""
        return
    def dbgLib(self, lib, fmt, *args):
        if os.path.basename(lib) == self.dbgLibName:
            print "%s : %s" % (os.path.basename(lib), fmt % args)
            
global rimcore 
rimcore=Rimcore()

#
# Variable management
#
class Variables(Rimcore):

    #
    # Names of special variables that are cummulative 
    #
    specVars="""
        __LIBS__
        __LIBSDIRS__ 
        __INCSDIRS__
        __LDFLAGS__""".split() 

    def initVars(self, obj=None):
        if obj:
            self.env=obj.env;
        else:
            try:
                self.env.vars={}
            except:
                self.env=Environment.Environment();
                self.env.vars={}
        
    def getChildrenByTagName(self, node, tagName):
        matches=[]
        for child in node.childNodes:
            if child.nodeType==child.ELEMENT_NODE and (child.tagName==tagName):
                matches.append(child)
        return matches
        
    def copyEnvVars(self, env):
        myenv=env.Clone();
        myvars=env.vars.copy()
        myenv.vars=myvars
        return myenv
            
    def addVar(self, name, value):
        if value == 'ENV':
            # fetch from environment
            if os.environ.has_key(name):
                value=os.environ[name]
            else:
                print "Variable '%s' cannot be found in environement" % name
                self.bt()
                sys.exit(1)
        if name in self.specVars:
            if not self.env.vars.has_key(name):
                self.env.vars[name]=self.translate(value)
            else:
                self.env.vars[name]+=" "+self.translate(value)
        else:
            self.env.vars[name]=self.translate(value)
        #print "    %s=%s" % (name, self.env.vars[name])
        
    def addVars(self, frm, to, show=0):
        for kv in frm.env.vars:
            if show:
                print "    %s=%s" % (kv,frm.env.vars[kv])
            to.addVar(kv,frm.env.vars[kv])

    def getVars(self, varNode, show=0):
        if show:
            print "Show is on!"
        for var in self.getChildrenByTagName(varNode, 'var'):
            name=var.getAttribute('name')
            value=var.getAttribute('value')
            if show:
                print "    %s=%s" % (name,value)
            self.addVar(name, value)

    def getVar(self, name, fail=0):
        if self.env.vars.has_key(name):
            return self.env.vars[name]
        else:
            if fail:
                print "Variable '%s' is not defined." % (name)
                print "Known variables are:"
                self.printVars();
                rimcore.bt(20)
                sys.exit(1)
            else:
                return None

    def varsToFile(self, file, indent=""):
        for var in self.env.vars:
            file.write("%s%s=\"%s\"" % (indent, var, self.env.vars[var]))

    def printVars(self):
        for var in self.env.vars:
            print "   %s=%s" % (var, self.env.vars[var])

    def parsePsizes(self, pstr):
        list=[]
        for val in pstr.split(':'):
            value=0
            if len(val) > 0:
                format=val[-1].upper()
                # default to megs
                factor=1024
                lastIdx=len(val)-1
                if format == 'K':
                    factor=1
                if format == 'M':
                    factor=1024
                elif format == 'G':
                    factor=1024*1024
                elif format == 'T':
                    factor=1024*1024*1024
                else:
                    lastIdx+=1
                value=int(val[:lastIdx]) * factor
            list.append(value)
        return list
            

    def translate(self, s):
        try:
            if type(s) != type(list()):
                s=Template(s).substitute(self.env.vars)
            else:
                s=(Template(string.join(s)).substitute(self.env.vars)).split()
        except KeyError, inst:
            self.dbglevel(0, True);
            self.dbg(0, "Error: Variable not found %s in '%s'", inst.args[0], s)   
            print "Known variables are:"
            self.printVars();
            rimcore.bt(20)
            sys.exit(1)
        return s
