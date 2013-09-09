#
# Set of functions to digest the init.d script files along with
# their declared dependencies.
#
#

import os
import sys
import subprocess

LEVELS      ='levels'
REQUIRES    ='requires'
PROVIDES    ='provides'
RESTARTS    ='restarts'
NAME        ='name'
CHILDREN    ='children'

#
# read a single rc file 
#
def getConfig(File, name):
    inside=False
    cfg={}
    cfg[NAME]=name
    cfg[LEVELS]=[]
    cfg[REQUIRES]=[]
    cfg[PROVIDES]=[]
    cfg[RESTARTS]=[]
    cfg[CHILDREN]=[]
    line=File.readline()
    while len(line):
        if line == "### BEGIN INIT INFO\n":
            inside=True
        elif line == "### END INIT INFO\n":
            break
        elif inside:
            fields=line.split(":")
            if len(fields) > 1:
                attr=fields[0].split()[-1]
                values=fields[1].split()
                if attr.lower() == "provides":
                    for v in values:
                        cfg[PROVIDES].append(v)
                elif attr.lower() == "required-start":
                    for v in values:
                        cfg[REQUIRES].append(v)
                elif attr.lower() == "restart-with":
                    for v in values:
                        cfg[RESTARTS].append(v)
                elif attr.lower() == "default-start":
                    for v in values:
                        cfg[LEVELS].append(v)
        line=File.readline()
    if inside:
        return cfg
    return None

#
# read in all configs for all script in supplied path
#
def getRcFiles(level, path):
    scripts = os.listdir(path)
    entries={}
    for script in scripts:
        fpath="%s/%s" % (path, script)
        if os.path.isfile(fpath):
            cfg=getConfig(open(fpath, "r"), script)
            if cfg:
                if level in cfg[LEVELS]:
                    entries[script]=cfg;
            else:
                # all rc* scritps are for rc management purpose itself
                # so no config is expected in these files.
                if script[0:2] != "rc":
                    print "Warning: no config found for file %s" % script
    return entries

#
# print the dependency tree
#
def prdeps(node, level=0):
    print "%s%s" % (" "*level*4, node[NAME])
    for child in node[CHILDREN]:
        prdeps(child, level+1)

def allMet(provided, required):
    for req in required:
        if req not in provided: return False
    return True
    
#
# get an ordered list of scripts in terms of when they need to be started
#
def getOrderedList2(entries):
    newProvision=True
    provided=[]
    order=[]
    while newProvision:
        newProvision=False
        for key in entries:
            if key in order: continue
            node=entries[key]
            if allMet(provided, node[REQUIRES]):
                order.append(key)
                for provide in node[PROVIDES]:
                    if provide not in provided:
                        provided.append(provide)
                        newProvision=True
    return order

#
# find which script supplied a certain service
#
def whoSupplies(entries, service, level):
    whos=[]
    for k in entries:
        if service in entries[k][PROVIDES]: 
            whos.append(k)
    if len(whos): 
        # if there are more then one suppliers of that service
        # we pick the first and make it dependant on a indexed name of that
        # service
        for idx in range(1,len(whos)):
            e=entries[whos[idx]]
            del(e[PROVIDES][e[PROVIDES].index(service)])
            e[PROVIDES].append("%s%d" % (service, idx))
            entries[whos[0]][REQUIRES].append("%s%d" % (service, idx))
        return whos[0]
    print "Could not find script supplying service '%s' @ init level %s" % (service, level)
    for k in entries:
        print "%10s - %s" % (k, entries[k][PROVIDES])
    sys.exit(1)
    
#
# check for dangling scripts
#
def chkUnused(entries, olist):
    danglers=[]
    for e in entries:
        entry=entries[e]
        if entry[NAME] not in olist:
            danglers.append(entry[NAME])
    if len(danglers):
        print "*** Warning --- Unused rc scripts found : %s ****" % danglers

def addAllDeps(entries, script):
    s=entries[script]
    for k in entries:
        if k != script:
            for d in entries[k][PROVIDES]:
                if d not in s[REQUIRES]:
                    s[REQUIRES].append(d)
        
def getRcEntries(level, path="/etc/init.d", depKey=REQUIRES):
    entries=getRcFiles(level, path)
    if len(entries):
        olist=getOrderedList2(entries)
        finalScript=whoSupplies(entries, 'final%s' % level, level)
        addAllDeps(entries, finalScript)
        chkUnused(entries, olist)
        return entries, olist
    else:
        return {}, []

if __name__ == '__main__':
    entries, olist=getRcEntries('5', '/etc/init.d')
    prdeps(entries[whoSupplies(entries, 'final%s' % 5, 5)])
    print olist
    sys.exit(0)
