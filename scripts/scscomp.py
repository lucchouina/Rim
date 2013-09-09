#!/usr/bin/env python
"""
    This file implements the logic required to run scs commands against various 
    components of a product.
    
"""
import os, sys
import getopt
import string
import glob
import subprocess
import imp
from string import Template
import xml.dom.minidom
import Rim
import RimApp
from scsOps import *
from SCons import Environment

class ScsComp():

    def __init__(self, prodname=os.getenv("RIM_PRODUCT"), branchname=os.getenv("RIM_BRANCH")):
        env=Environment.Environment()
        env.vars={}
        self.rim=Rim.Rim(env, Rim.Rim.Shared);
        appFile="%s/App.xml" % os.path.dirname(__file__)
        appNode=xml.dom.minidom.parse(appFile).getElementsByTagName('application')[0]
        self.conf=RimApp.RimApp(appNode, self.rim, quiet=1)
        self.conf.branches=self.conf.rim.branches
        self.product=self.conf.products[prodname]
        self.branch=self.conf.branches[branchname]
        self.branchName=branchname
        # verify that product and branch are compatible
        self.allComps(self.compScsIsInBranch)

    def compScsIsInBranch(self, op, comp, compi):
        #
        # make sure this component is in the scope of this branch
        #
        if comp.root.scs not in self.branch.scs:
            print "No source tree '%s' found in branch '%s', needed for product '%s'" % (comp.root.scs, self.branchName, self.product.name)
            print "Either modify the branch specification file '%s'" % (self.branch.filename)
            print "Or select a different branch."
            sys.exit(1)
    #
    # replce .. in the subtrees.
    # svn cannot handle that. Terminate if we end up outside of the scs root
    #        
    def processDir(self, dir):
        dirs=dir.split('/')
        d2=[]
        l2=0
        level=0
        while level < len(dirs):
            if dirs[level] == '.': 
                level = level +1
                continue
            elif dirs[level] == '..':
                if l2 == 0:
                    print "Invalid subdir '%s' - refers outside of scs root" % dir
                    return False
                else: 
                    l2 = l2-1
                    level = level + 1
            else:
                d2.append(dirs[level])
                l2=l2+1
                level=level+1
        return string.join(d2, '/')
            

    def processDirs(self, dirs):
        newsubs=[]
        for dir in dirs:
            newsub=self.processDir(dir)
            if not newsub: return False
            newsubs.append(newsub)
        return newsubs
    #
    # Perform either of 'checkout', 'update', 'clean' or 'switch' on all
    # subtress associated with a component
    #
    def doCompOp(self, op, comp, compi):
        scs=self.conf.rim.scs[comp.root.scs]
        scsOps=ScsOps(self.conf, scs)   
        repo=self.conf.rim.repos[scs.repo]
        scstype=self.conf.rim.scstypes[repo.type]
        
        def chkSubDirs(psrc, pdst, src, dst):
            dst=dst[len(pdst)+1:]
            src=src[len(psrc)+1:]
            dirs=dst.split('/')
            dpath=""
            spath=""
            if len(dirs) < 2: return
            for didx in range(0, len(dirs)-1):
                dpath="%s/%s" % (dpath, dirs[didx])
                spath="%s/%s" % (spath, dirs[didx])
                ppos="%s/%s" % (pdst, dpath)
                spos="%s/%s" % (psrc, spath)
                # always check on directory down to know if we need to 
                # update the current one
                if not os.path.isdir("%s/%s" % (ppos, dirs[didx+1])):
                    scsOps.setDST(ppos)
                    scsOps.setTARGET(dirs[didx+1])
                    scsOps.setSRC(spos)
                    scsOps.setOPTIONS("--depth=empty")
                    scsOps.OpExec('checkout')

        # extract some of the variables that will populate the environment
        branch="%s%s" % (scs.prefix, self.branch.name)
        #
        # Each component has a component root
        # If the scs type supports subtree checkouts, we can checkout the
        # the component root's rim.py file and extract a sourceTress[] array 
        # which gives a list of relatiove directories to be checked out.
        # This is optional and if not found, we need to checkout this entire 
        # component root.
        #
        subtrees={}
        if scstype.subtrees:
            # try to get a rim.py
            # check that the root of this scs is checkouts to the destination
            # everything else will then be updates.
            dst="%s/%s" % (self.mkSroot(), scsOps.scsBranch)
            if not os.path.isdir(dst):
                scsOps.setSRC("")
                scsOps.setDST(dst)
                scsOps.setOPTIONS("--depth=empty")
                scsOps.OpExec('checkout')
            #
            # then take care of any intermediate subdirs to this component's
            # prefix
            #
            prefix=comp.root.prefix
            dst="%s/%s/%s" % (self.mkSroot(), scsOps.scsBranch, prefix)
            scsOps.createPath(self.mkSroot(), prefix)
            scsOps.setOPTIONS("")
            #
            # update the rim.py file (this is an optional file)
            # which at this time can give guidance on what we need
            # to check out for this component.
            #
            # We do not make this mechanism recursive at this point.
            # 
            scsOps.setDST("%s/%s" % (dst, "rim.py"))
            scsOps.setSRC("%s/%s" % (prefix, "rim.py"))
            scsOps.OpExec(op)
            dirList=[ prefix ]
            # did we get one?
            rimFile="%s/rim.py" % dst
            if os.path.isfile(rimFile):
                def MyImport(e):
                    return True
                import __builtin__
                __builtin__.Import=MyImport
                self.rim.env['QUIET']=True
                __builtin__.env=self.rim.env
                # check if it defines a list of directories
                mod=imp.load_source("rim", rimFile)
                dirList=[]
                if 'sourceTrees' in dir(mod):
                    if type(mod.sourceTrees) != type(list()):
                        if comp.name in mod.sourceTrees:
                            dirList=mod.sourceTrees[comp.name]
                    else:
                        dirList=mod.sourceTrees
                if not len(dirList): disList=[ "." ]
                else: 
                    dirList.append('rim') # add optional component spec directory
                    dirList=self.processDirs(dirList)
                    if not dirList:
                        print "Invalid directory found in '%s'" % rimFile
                        sys.exit(1)
                for d in dirList:
                    subtrees["%s/%s" % (prefix, d)]="%s/%s" % (dst, d)
            else:
                
                # no rim.py, check out the entire thing
                subtrees[prefix]=dst
                
            #
            # check that all intermediate directories have been created
            #
            for src in subtrees:
                chkSubDirs(prefix, dst, src, subtrees[src])

            if op == "merge":
                scsOps.setOPTIONS("--depth=infinity")
            else:
                scsOps.setOPTIONS("--set-depth=infinity")

        else:
            # all of it
            dst="%s/%s%s" % (self.mkSroot(), scsOps.dstPrefix, scsOps.scsBranch)
            subtrees[""]=dst
            print "git of %s" % dst
            if not os.path.isdir(dst):
                print "Doing checkout of %s" % dst
                os.system("mkdir -p %s" % dst)
                op="checkout"

        # go through the list we have made up
        if scs.archspecific:
            # we need to add a arch specific prefix
            newtrees={}
            for src in subtrees:
                key="%s/%s" % (src, compi.rootRelDir)
                value="%s/%s" % (subtrees[src], compi.rootRelDir)
                newtrees[key]=value
                if not os.path.isdir(value):
                    print "Doing checkout of %s" % dst
                    os.system("mkdir -p %s" % value)
                    op="checkout"
            subtrees=newtrees
        for src in subtrees:
            scsOps.setSRC(src)
            scsOps.setDST(subtrees[src])
            scsOps.OpExec(op)
            
    #
    # Perform an OP on all components
    #
    def forAllComps(self, op):
        self.allComps(self.doCompOp, op)
    #
    # loop over all components which are part of the current product
    # calling a callback function for each
    #
    def allComps(self, callback, op=None):
        nodes=self.product.nodes
        done=[]
        for nodeK in nodes:
            node=nodes[nodeK]
            compis=nodes[nodeK].compis
            for compK in compis:
                compi=compis[compK]
                compname=compi.name
                comp=self.conf.components[compname]
                if not compname in done:
                    callback(op, comp, compi)
                    done.append(compname)

    def mkSroot(self):
        return "%s" % (os.getenv("RIM_WORKSPACE"))
    #
    # check if a branch root is available locally and create it if not
    # asking user. This means checking out all of the components
    # for the associated product.
    #
    # So - better ask....
    #
    def chkSroot(self, forced=False):
        sroot=self.mkSroot(self.branch.name)
        if not os.path.isdir(sroot):
            out("Local copy of '%s' not found." % branch)
            if forced or not yn_choice("Would you like to create it?", default="n"):
                # create the branch root
                try: os.mkdir(sroot) 
                except: pass
                return forAllComps(product, checkItOut, branch)
            return False
        return True

