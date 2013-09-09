#!/usr/bin/env python
import os
import sys
import xml.dom.minidom
import Rim
import RimApp
from SCons import Environment

env=Environment.Environment()
env.vars={}
rim=Rim.Rim(env, Rim.Rim.Shared);

# read in the entire configuration for that app and site
mypath="/".join(os.path.abspath(__file__).split("/")[0:-1])
appFile="%s/App.xml" % mypath
appNode=xml.dom.minidom.parse(appFile).getElementsByTagName('application')[0]
conf=RimApp.RimApp(appNode, rim, quiet=1)

def showProducts():
    print "Available products are:"
    for proc in conf.products:
        print "    %s" % prod

def showBranches():
    print "Available branches are:"
    for ranch in conf.branches:
        print "    %s" % branch

def listBranches(details=False, args=[]):
    
    for cskey in sorted(conf.rim.branches):
        branch=conf.rim.branches[cskey]
        if not len(args) or branch.name in args:
            if details: print "Branch - ",
            print  "%-20s -%10s : %s" % (branch.name, branch.product, branch.desc)
            if details:
                print "    Source trees:"
                for sk in branch.scs:
                    parent=""
                    revision=""
                    if len(branch.parents[sk]) > 0:
                        parent=" parent [ %10s ]" % branch.parents[sk]
                    if len(branch.revision[sk]) > 0:
                        revision=" revision [ %10s ]" %branch.revision[sk]
                    print "     %12s - version %10s%s%s" % (sk, branch.scs[sk], revision, parent)
                print
            
def chkBranch(branchname, verbose=False):
    if not branchname in conf.rim.branches:
        print "Branch '%s' not found" % branchname
        return False
    return True

def chkEnv(Prod=True, Branch=False):

    if Prod:
        # check if product has been specified
        prodname=os.getenv("RIM_PRODUCT")
        if not prodname:
            print "$RIM_PRODUCT environment variable is not defined."
            showProducts()
            sys.exit(1)

        if prodname not in conf.products:
            print "Product '%s' defined in environment variable $RIM_PRODUCT was not found." % prodname
            showProducts()
            sys.exit(1)

    if Branch:
        # check if product has been specified
        branchname=os.getenv("RIM_BRANCH")
        if not branchname:
            print "$RIM_BRANCH environment variable is not defined."
            listBranches()
            sys.exit(1)
        if not chkBranch(branchname):
            print "Branch '%s' defined in environment variable $RIM_BRANCH was not found." % branchname
            listBranches()
            sys.exit(1)


