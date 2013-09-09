import os, stat
import copy
import sys
#import glob
import re
import time
import RimUtils
import RimCore
import RimLib
import xml.dom.minidom
from string import Template
from SCons import Node

class modItem:
    def __init__(self, mod, elnode=0, owner=None, group=None):
        if elnode:
            self.source=mod.translate(elnode.getAttribute("source"));
            self.target=elnode.getAttribute("target") or self.source;
            self.target=mod.translate(self.target);
            self.perms=elnode.getAttribute("perms") or "0755";
            self.type=elnode.getAttribute("type") or "file";
            self.skip=[]
            skip=elnode.getAttribute("skip") 
            if skip:
                self.skip = skip.split(",");
            self.recurse=elnode.getAttribute("recurse");
            self.shadow=elnode.getAttribute("shadow");
            self.show=elnode.getAttribute("show") or "0";
            self.arches=elnode.getAttribute("arch") or "";
            self.versions=elnode.getAttribute("version") or "";
            self.releases=elnode.getAttribute("release") or "";
            self.arches=self.arches.split();
            self.versions=self.versions.split();
            self.mask=elnode.getAttribute("mask");
            self.nolibs=elnode.getAttribute("nolibs");
            self.major=elnode.getAttribute("major") or "0";
            self.minor=elnode.getAttribute("minor") or "0";
            self.nodetype=elnode.getAttribute("nodetype") or "c";
            self.cpu=elnode.getAttribute("cpu");
            self.applibs=elnode.getAttribute("appLibs");
            self.owner=mod.translate(elnode.getAttribute("owner") or owner or "0");
            self.group=mod.translate(elnode.getAttribute("group") or group or "0");
            self.nolink=False;
            if self.show=="1":
                print "%s -> %s" % (self.source, self.target)
    
    def getDevInfo(self, s):
        self.major="%d" % (os.major(s.st_rdev))
        self.minor="%d" % (os.minor(s.st_rdev))

    def updateFromStat(self, s):
        mode=s.st_mode
        self.perms="%04o" % (mode & 0xfff);
        if stat.S_ISDIR(mode):
            self.type="dir"
        if stat.S_ISCHR(mode):
            self.type="node"
            self.nodetype="c"
            self.getDevInfo(s)
        if stat.S_ISBLK(mode):
            self.type="node"
            self.nodetype="b"
            self.getDevInfo(s)
        if stat.S_ISREG(mode):
            self.type="file"
        if stat.S_ISLNK(mode) and not self.nolink:
            self.type="link"
            self.source=os.readlink(self.paths[0])
        
def printModule(cmd, target, source, env):
    return

class module(RimCore.Variables):
    elements={}
    sources=[]
    indent="                        "
    def __init__(self, modXmlNode, spec):
        #print "module.__init__ checkpoint A: %s" % time.asctime()
        self.env=spec.env
        self.getVars(modXmlNode);
        self.name=self.translate(modXmlNode.getAttribute("name"));
        self.owner=self.translate(modXmlNode.getAttribute("owner"));
        self.group=self.translate(modXmlNode.getAttribute("group"));
        self.elements={}
        self.scriptText={}
        self.scriptRank={}
        self.sources=[]
        self.reqs=[]
        self.knode=0
        self.pnode=0
        self.unode=0
        self.spec=spec
        # open an interface to librrary management class
        #print "module.__init__ checkpoint B: %s" % time.asctime()
        self.lHdl=RimLib.rimLibHandle(self.env.amfi, self)
        #
        # use specified filesystem type for this module
        self.fstype=modXmlNode.getAttribute("fs")
        self.level=modXmlNode.getAttribute("level")
        if not self.level:
            self.level=255
        else:
            self.level=int(self.level)
        self.prime=modXmlNode.getAttribute("prime")
        if not self.prime:
            self.prime=0
        else:
            self.prime=int(self.prime)
        self.version=modXmlNode.getAttribute("version")
        if not self.version:
            print "Version missing for module '"+self.name+"'"
            sys.exit(1)
            
        # if not specified then fall back to the default for that os
        #print "module.__init__ checkpoint C: %s" % time.asctime()
        if not self.fstype:
            self.fstype=self.env.amfi.os.fstype
        if not self.fstype:
            print "File system type was not specified for module '"+self.name+"'"
            print "And no Os fstype specified for os '"+self.env.amfi.os.name+"'"
            sys.exit(1)
        if not self.env.amfi.os.fsbuilders.has_key(self.fstype):
            print "Invalid File system type '"+self.fstype+"' was not specified for module '"+self.name+"'"
            sys.exit(1)
        #
        # Stash the attributes of that module
        self.bootable=modXmlNode.getAttribute("bootable") or "0"
        self.isRequired=modXmlNode.getAttribute("required") or "0"
        #
        # Go through the element an dpossibly recurse of includes includes
        #print "module.__init__ checkpoint D: %s" % time.asctime()
        self.processElements(modXmlNode, {})
        #
        # Make a list of the requirements and make sure we find those modules in
        # the associated osRelease+Arch root.
        #
        for requirement in modXmlNode.getElementsByTagName('requires'):
            rname=requirement.getAttribute('name')
            RimCore.rimcore.dbg(2, self.indent+"    Required module for '%s' is '%s'",self.name,rname)
            #
            # XXX need to add this requirement to the list (rim.modules{})
            self.reqs.append(rname)
        #
        # Extract all of the scripts that have been defined for that module
        #
        snodes = modXmlNode.getElementsByTagName('script')
        for snode in snodes:
            context=snode.getAttribute('context')
            self.scriptText[context]=snode.firstChild.wholeText
            self.scriptRank[context]=snode.getAttribute('rank')
            
    def processElements(self, xmlNode, curlist={}):
        #
        # Read in all of the elements for that module
        for elNode in xmlNode.getElementsByTagName('element'):
            mi=modItem(self, elNode, self.owner, self.group)
            if len(mi.arches) and self.env.amfi.arch.name not in mi.arches:
                continue
            if len(mi.releases) and self.env.amfi.os.name not in mi.releases:
                continue
            if len(mi.versions) and self.env.amfi.version not in mi.versions:
                continue
            if mi.type != "link" and mi.type != "node" and mi.type[0:5] != "empty":
                # find a final location for that source files
                mi.paths=self.env.compi.findFile(mi.source, mi.applibs, 0, mi.show=="1")
            self.explode(mi, show=(mi.show=="1"))
        for incNode in xmlNode.getElementsByTagName('include'):
            sname=self.translate(incNode.getAttribute('spec'))
            # if path is relative, prepend surrent spec path
            if sname[0] != '/' :
                spath=os.path.dirname(self.spec.path)+'/'+sname
            else :
                spath=sname
            # take care of include recursions
            if not curlist.has_key(sname) :
                curlist[sname]=1
                RimCore.rimcore.dbg(2, self.indent+"    Including file'%s' is '%s'",self.name,sname)
                if os.path.isfile(spath):
                    # add the path fo the spec itself as a candidate for roots
                    
                    dpath=os.path.dirname(spath)
                    RimCore.rimcore.dbg(8, "prepending to self(%s).env.amfi.roots: %s", self.name, dpath)
                    self.env.compi.roots.insert(0,dpath)
                    RimCore.rimcore.dbg(8, "self(%s).env.amfi.roots = %s", self.name, self.env.compi.roots)
                    self.processElements(xml.dom.minidom.parse(spath), curlist)
                    RimCore.rimcore.dbg(8, "shifting from self(%s).env.amfi.roots: %s", self.name, self.env.compi.roots[-1])
                    self.env.compi.roots.pop(0)
                    RimCore.rimcore.dbg(8, "self(%s).env.amfi.roots = %s", self.name, self.env.compi.roots)
                else:
                    print "Include not found in module spec '%s' : %s" % (self.name, sname)
                    sys.exit(1)
    
    # used only by the bom.var.sh target file to add that compiled file to the 
    # bootabble module of a target node
    #
    def addElement(self, source, target):
        mi=modItem(self)
        mi.type="file"
        mi.source=source
        mi.target=target
        mi.path=source
        mi.perms="0644"
        mi.nolink=True
        mi.owner="0"
        mi.group="0"
        self.elements[mi.target]=mi
        self.env.Depends(self.bnode, self.env.File(mi.path))

    def explode(self, mi, isGlob=0, skip=None, show=0):
        if self.elements.has_key(mi.target) and mi.type != "dir":
            if isGlob == 0 or mi.shadow == 0:
                print "Found duplicate for target %s:" % mi.target
                print "     source : "+mi.source
                print "     target : "+mi.target
                print "     type   : "+mi.type
                print "Duplicate  found in module : %s" % self.name
                print "Originally found in module : %s" % self.elements[mi.target].mname
                sys.exit(1)
            RimCore.rimcore.dbg(8, "skipping %s: already found %s", mi.source, mi.target )
            return

        # Add it
        self.elements[mi.target]=mi
        if show == 1:
            dbgLevel=0
        else:
            dbgLevel=2
        #
        # remember the coordinates to help with dups
        #
        mi.mname=self.name
        if mi.type == "file" and mi.paths[0]:
            mi.path=mi.paths[0]
            #
            # If this element if specifying a dependency on a specific appLib then
            # push it here so that the library management core can find all the 
            # library it needs.
            #
            if mi.applibs:
                print "Applibs=%s" % mi.applibs
                self.addAppLibs(mi.applibs)
                
            RimCore.rimcore.dbg(dbgLevel, "File - %s", mi.path)
            self.sources.append(self.env.Entry(mi.path.replace('$','$$')))
            isLib=False
            if not mi.nolibs:
                # let the lib interface check out the dependencies
                try:
                    stats=os.lstat(mi.path)
                    isLib=mi.path[-3:]==".so"
                except:
                    RimCore.rimcore.dbg(dbgLevel, "Explode - caught exception on '%s'", mi.path)
                else:
                    # we only processed files that have been marked as executable
                    if (stats.st_mode & stat.S_IXUSR) or isLib:
                        self.lHdl.addLibs(mi.path, self.env.compi.findLib, self.level, self.prime)
        #
        # We check for recursions here.
        elif mi.type == "dir":
            RimCore.rimcore.dbg(dbgLevel, "Dir - %s", mi.paths)
            RimCore.rimcore.dbg(dbgLevel, "    shadow = %s", mi.shadow)
            paths = [ mi.paths[0] ]
            if mi.shadow:
                paths = mi.paths
            RimCore.rimcore.dbg(dbgLevel, "    mask = '%s'", mi.mask)
            if mi.mask :
                if mi.mask == "*": # special case for backwards compatibility with glob patterns
                    mi.mask = ".*"
                if len(mi.skip):
                    cskip=[]
                    if skip:
                        cskip += skip
                    for mask in mi.skip:
                        cskip.append(re.compile(mask))
                else:
                    cskip=skip
                mask = re.compile(mi.mask)
                for path in paths:
                    try:
                        matches=os.listdir(path)
                    except:
                        print "Directory error on '%s' in spec '%s'" % (mi.source, self.spec.name)
                    for match in os.listdir(path):
                        if match in [ ".svn", "rim", ".gitit" ]:
	                        continue;
                        if not mask.match(match):
                            continue
                        doskip=0
                        if cskip:
                             for cexp in cskip:
                                if cexp.match(match) :
                                    doskip=1
                                    break
                        if doskip:
                            continue
                        # skip over unicode for now
                        try:
                            match = path+'/'+match
                        except:
                            continue
                        RimCore.rimcore.dbg(dbgLevel, "Match - '%s'", match)
                        stats=os.lstat(match)
                        mode=stats.st_mode
                        if not mi.recurse and stat.S_ISDIR(mode):
                            # skip it - we're not recursing
                            continue 
                        newmi=copy.deepcopy(mi)
                        newmi.paths=[match]
                        newmi.source += match[len(path): ]
                        newmi.target += match[len(path): ]
                        newmi.updateFromStat(stats)
                        self.explode(newmi, 1, cskip, show=show)

    def addLibDeps(self):
        #
        # We are ready to insert our dependencies into the tree
        #
        menv=self.spec.env.Clone()
        menv.module=self
        menv.artifacts=self.spec.prod.artifacts
        #
        #    Need to add the libary dependencies for this module.
        #    The scanning process has happened and the proper library have been 
        #    associated with their respective module based on the module level or layer
        #    explained in RimLib.py
        #    
        #    We simply call into the lib API and ask for all libraries that have been assigned to us.
        myList=self.lHdl.myLibs()
        RimCore.rimcore.dbg(2, "Adding the following libs to module '%s' variant '%s':", self.name, menv.amfi.modext)
        for ltuple in myList:
            (libpath, relpath)=ltuple
            newmi=modItem(self)
            newmi.type="file"
            newmi.source=relpath
            newmi.target=relpath
            newmi.path=libpath
            newmi.perms="0755"
            newmi.nolink=True
            newmi.owner=self.owner or "0"
            newmi.group=self.group or "0"
            if self.elements.has_key(newmi.target):
                print "Duplicate library entry for  : "+newmi.path
                print "source : "+newmi.source
                print "target : "+newmi.target
                print "In module : "+self.name
                print "Spec      : %s" % (self.spec.path)
                sys.exit(1)
            self.elements[newmi.target]=newmi;
            RimCore.rimcore.dbg(2, "    %s - %s", libpath, relpath);
            self.sources.append(self.env.Entry(libpath))
        #
        # Now that we do have all files for that module - register the dependancy
        #
        targetFsName="%s/%s-%s%s.fs" % (self.spec.prod.artifacts, self.name, self.version, menv.amfi.modext)
        menv['PRINT_CMD_LINE_FUNC']=printModule
        self.bnode=menv.Module(targetFsName, self.sources)
        self.bnode.mod=self
        #
        # add the spec file itself as a dependancy of the module.
        #
        menv.Depends(self.bnode, menv.File(self.spec.path))
        #
        # if this module is bootable (e.g. initrd in Linux parlance)
        # make a kernel available as well in the distro
        #
        if self.bootable == "1" :
            kpaths=menv.compi.findFile("/boot/kernel."+menv.amfi.name, 0, 1, 0)
            if not kpaths[0]:
                kpaths=menv.compi.findFile("/boot/kernel."+menv.amfi.clm.name, 0, 1, 0)
                if not kpaths[0]:
                    kpaths=menv.compi.findFile("/boot/kernel", 0, 1, 0)
                    if not kpaths[0]:		
                        print "Kernel file not found for CLM [%s]" % menv.amfi.clm.name
                        print "Kernel file not found for AMF[%s]" % menv.amfi.name
                        menv.compi.findFile("/boot/kernel", 0, 1, 1)
                        sys.exit(1)
            knode=menv.File(kpaths[0])
            # print "Install %s ad %s" % (kpaths[0], self.spec.prod.artifacts+"/kernel"+menv.amfi.modext)
            self.knode=menv.InstallAs(self.spec.prod.artifacts+"/kernel"+menv.amfi.modext, knode)
            #
            # For uboot nodes, that means we also need the preloader and uboot
            #
            if menv.amfi.clm.loader == "uboot":
                upaths=menv.compi.findFile("/boot/u-boot."+menv.amfi.clm.name, 0, 1, 0)
                if not upaths[0]:
                    upaths=menv.compi.findFile("/boot/u-boot", 0, 1, 0)
                    if not upaths[0]:		
                        print "u-boot file not found for CLM [%s]" % menv.amfi.clm.name
                        menv.compi.findFile("/boot/u-boot", 0, 1, 1)
                        sys.exit(1)
                ublnode=menv.File(upaths[0])
                self.unode=menv.InstallAs(self.spec.prod.artifacts+"/u-boot"+menv.amfi.modext, ublnode)
                ptype=menv.amfi.clm.preloader
                ppaths=menv.compi.findFile(("/boot/%s.%s" % (ptype, menv.amfi.clm.name)), 0, 1, 0)
                if not ppaths[0]:
                    ppaths=menv.compi.findFile(("/boot/%s" % ptype), 0, 1, 0)
                    if not ppaths[0]:		
                        print "%s file not found for CLM [%s]" % (ptype, menv.amfi.clm.name)
                        menv.compi.findFile(("/boot/%s" % ptype), 0, 1, 1)
                        sys.exit(1)
                pnode=menv.File(ppaths[0])
                self.pnode=menv.InstallAs(self.spec.prod.artifacts+("/%s" % ptype)+menv.amfi.modext, pnode)
                
            
        
class RimSpec(RimCore.Variables):
    indent="                    "
    def __init__(self, path, name, obj, prod):
        self.env=self.copyEnvVars(obj.env)
        self.obj=obj
        self.path=path
        self.name=name
        self.modules={}
        self.amfis=[]
        self.prod=prod
        RimCore.rimcore.dbg(2, self.indent+"Found spec file - %s", path)
        #
        # load the xml
        self.specRoot=xml.dom.minidom.parse(path);
        #
        # spec file variables
        #
        self.getVars(self.specRoot.getElementsByTagName('spec')[0])
        
    def init(self, reqs):
        #
        # process the module definitions
        self.reqs=[]
        ret=False
        for modNode in self.specRoot.getElementsByTagName('module'):
            mname=modNode.getAttribute('name')
            required='required' in modNode.getAttribute('flags').split()
            RimCore.rimcore.dbg(2, self.indent+"Module - %s - required %s reqs %s" % (mname, required, reqs))
            #
            # record the new module
            if required or (mname in reqs):
                mod=module(modNode, self)
                self.modules[mod.name]=mod
                self.reqs+=mod.reqs
                ret=True
        return ret
            
            
    def addAmfi(self, amfi):
        self.amfis.append(amfi)
        for modKey in self.modules:
            self.prod.addAmfiToModule(self.modules[modKey], amfi)
        
        
    def getModules(self):
        return self.modules

#
# Class to track spec files
# As components are processed, more then one can point to the same set of modules
# and arch+os+os_version combo. This class will track that.
#
class specTracker:
    def __init__(self, prod):
        self.spectab={}
        self.prod=prod
    # callers passes the name for that spec and its current amf instance 
    def processSpec(self, root, name, obj, reqs=[], show=1):
        if not os.environ.has_key('RIM_PACKAGES') :
            return []
        # check for the presense of a spec file in the root/rim directory
        # We first look for a file with the component's name, then rim.spec
        path="%s/%s.spec" % (root, name)
        if not os.access(path, os.R_OK):
            path="%s/rim.spec" % (root)
            if not os.access(path, os.R_OK):
                if show:
                    RimCore.rimcore.dbg(0,  "                    Spec file '%s' not found.",path)
                return []

        # found a spec
        RimCore.rimcore.dbg(2, "                    spec - %s",path)
        amfi=obj.env.amfi
        os.environ['OS']=amfi.os.name
        fullName=name+'_'+amfi.distro.name+'_'+amfi.version+'_'+amfi.arch.name
        if self.spectab.has_key(fullName) :
            spec=self.spectab[fullName]
        else:
            # add it
            spec=RimSpec(path, name, obj, self.prod)
            if spec.init(reqs):
                self.spectab[fullName]=spec
            else:
                return []
        # add this amfi to that spec
        spec.addAmfi(amfi)
        return spec.reqs

    def specTab(self):
        return self.spectab
