#!/usr/bin/env python
"""
    Common functions between rimview and rimbranch
    
"""

from string import Template
import os, sys
import subprocess

class ScsOps():

    def __init__(self, conf, scs, product=os.getenv("RIM_PRODUCT"), branch=os.getenv("RIM_BRANCH")):
        self.env={}
        self.name=scs.name
        self.conf=conf
        self.scs=scs
        self.repo=conf.rim.repos[self.scs.repo]
        self.scstype=conf.rim.scstypes[self.repo.type]
        self.product=product
        self.branchName=branch
        branch=conf.rim.branches[self.branchName]
        self.branch=branch
        #
        # make sure this component is in the scope of this branch
        #
        if self.name not in branch.scs:
            print "No source tree '%s' found in branch '%s', needed for product '%s'" % (self.name, self.branchName, self.product)
            print "Either modify the branch specification file '%s'" % (branch.filename)
            print "Or select a different branch."
            sys.exit(1)
        prefix=scs.prefix
        if not prefix:
           self.dstPrefix=self.name+"_"
        else:
           self.dstPrefix=""
        self.scsBranch="%s%s" % (prefix, branch.scs[self.name])
        if len(branch.parents[self.name]) > 0:
            self.env["PARENT"]="%s%s" % (prefix, branch.parents[self.name])
        else:
            self.env["PARENT"]=""
        self.env["REVISION"]=branch.revision[self.name]
        self.version=branch.scs[self.name]
        self.env["BRANCH"]=self.scsBranch
        self.env["PRODUCT"]=self.product
        self.env["TYPE"]=self.repo.type
        self.env["ROOT"]=self.repo.root
        self.env["SERVER"]=self.repo.server
        self.env["CONTYPE"]=self.repo.contype
        self.env["PORT"]=self.repo.port
        self.env["SCSNAME"]=self.name
    
    def scsDstRoot(self):
        return "%s/%s%s%s"  % (self.conf.rim.workspace, self.dstPrefix, self.scs.prefix, self.version)
        
    def createPath(self, root, path):
        # check the root
        allDirs=("/%s" % (path)).split("/")
        src=""
        dst="%s/%s" % (root, self.scsBranch)
        for  subdir in allDirs:
            # for now, only svn can do this.
            dst="%s/%s" % (dst, subdir)
            src="%s/%s" % (src, subdir)
            # try to update the directory and its immediates
            self.setSRC(src)
            self.setDST(dst)
            self.setOPTIONS("--depth=immediates")
            self.OpExec("update")
        

    # settings hooks
    def setSRC(self, src): self.env["SRC"]=src
    def setDST(self, dst): self.env["DST"]=dst
    def setOPTIONS(self, options): self.env["OPTIONS"]=options
    def setSRC(self, src): self.env["SRC"]=src
    def setTARGET(self, target): self.env["TARGET"]=target
    
    def Url(self, version=None):
        if not version: version=self.version
        return "%s://%s:%s/%s/%s%s" % (
        self.env["CONTYPE"],
        self.env["SERVER"],
        self.env["PORT"],
        self.env["ROOT"],
        self.scs.prefix,
        version
        )
    
    def ChkBranch(self, branchName):
        self.env['BRANCH']=branchName
        self.env['DST']=branchName
        self.env['PREFIX']=self.scs.prefix
        return self.OpExec('chkbranch')
    
    def ChkServer(self, branchName):
        self.env['BRANCH']=branchName
        self.env['DST']=branchName
        self.env['PREFIX']=self.scs.prefix
        return self.OpExec('chkserver')
    
    def Revision(self):
        return self.OpExec('revision',keepOutput=True)
    
    def View(self):
        return self.OpExec('view',keepOutput=True)
    
    def Update(self, branchName):
        self.env['BRANCH']=branchName
        return self.OpExec('update')
    
    def MkBranch(self, newbranch, branch, msg):
        self.env['BRANCH']=newbranch
        self.env['DST']=newbranch
        self.env['PARENT']=branch
        self.env["PREFIX"]=self.scs.prefix
        self.env['MSG']=msg
        #print "%-12s %12s: %10s : creating branch '%12s' from '%12s'"  % (
        #    self.env["TYPE"],
        #    self.env["SERVER"],
        #    self.scs.name,
        #    "%s%s" % (self.env["PREFIX"], self.env['BRANCH']),
        #    "%s%s" % (self.env["PREFIX"], self.env['PARENT']))
        return self.OpExec('mkbranch')
        
    def RmBranch(self, branch, msg):
        self.env['BRANCH']=branch
        self.env['MSG']=msg
        self.env["PREFIX"]=self.scs.prefix
        return self.OpExec('rmbranch')
        
    #
    # execute a single operation from the scs hooks
    #
    def OpExec(self, op, keepOutput=False):
        action=self.conf.rim.scstypes[self.env["TYPE"]].actions[op]
        tpl=Template(action.script)
        if 'TARGET' in self.env: target="/%s" % self.env['TARGET']
        else : target=""
        if op == 'update' or op == 'checkout':
            print "%s %s[%s]" % (op, self.env['DST'], target)
        #print "Script after = \n%s\n" % tpl.substitute(self.env)
        child=subprocess.Popen("%s" % action.interpreter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        try:
            child.stdin.write(tpl.substitute(self.env))
        except:
            print "Error with variable substitution in block:"
            print action.script
            raise
        child.stdin.close()
        buf=""
        line=child.stdout.readline()
        while len(line):
            buf = buf + line
            line=child.stdout.readline()
        #raw_input("Hit 'return'")
        exitCode=child.wait()
        if keepOutput:
            if exitCode == 0:
                return buf.split('\n')[0]
            else:
                return "!!error!!"
        else:
            return True if exitCode == 0 else False
