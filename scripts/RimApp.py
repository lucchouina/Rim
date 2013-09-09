import os
import glob
import sys
import copy
import string
import imp
import xml.dom.minidom
from string import Template

import Rim
import RimSpec
import RimCore

def replace(s, p1, p2):
    lst=s.split()
    lst2=[]
    for tok in lst:
        if tok==p1:
            lst2.append(p2)
        else:
            lst2.append(tok)
    return string.join(lst2)

libPaths=[ '/lib', '/usr/lib' ]

class Buildroot:
    def __init__(self, rootNode, comp):
        self.prefix=comp.translate(rootNode.getAttribute('prefix'))
        self.scs=rootNode.getAttribute('scs')
            
class Component(RimCore.Variables):
    def __init__(self, compNode, app):
        self.env=self.copyEnvVars(app.env)
        self.name=compNode.getAttribute('name')
        self.getVars(compNode)
        self.root=Buildroot(compNode.getElementsByTagName('buildroot')[0], self)
        RimCore.rimcore.dbg(2, "component - %s\n", self.name)

class Key():
    def __init__(self, node):
        self.name=node.getAttribute('action')
        self.text=node.firstChild.wholeText

#
# amf node instance. A useful object that we create while
# processing services of the application and that combines a number
# of other objects (release, clm, arch, component)
class AmfInstance(RimCore.Variables):
        
    def __init__(self, amfNode, rim):
        self.env=self.copyEnvVars(rim.env) 
        self.getVars(amfNode)
        self.name=amfNode.getAttribute('name')
        try:
            self.clm=rim.clms[amfNode.getAttribute('clm')]
        except:
            print "Clm node type not found '%s', while processing Amf node %s" % (amfNode.getAttribute('clm'), self.name)
            sys.exit(1)
        try:
            self.distro=rim.distros[amfNode.getAttribute('distro')]        
        except:
            print "Os disro not found '%s', while processing Amf node %s" % (amfNode.getAttribute('distro'), self.name)
            sys.exit(1)
        self.version=amfNode.getAttribute('distroVersion')
        self.os=rim.oses[self.distro.osBase]
        self.isCtr=amfNode.getAttribute('isControlNode')
        self.arch=rim.arches[self.clm.arch]
        RimCore.rimcore.dbg(2, "initializing self(amfNode %s).roots to rim.roots: %s", self.name, rim.roots)
        tname=self.distro.versions[self.version][self.arch.name].tools
        self.tools=rim.toolsets[tname]
        self.rootPath=rim.getVar("rootsRoot")
        # Record that one for later use
        customRoot=rim.getVar("customRoot")
        self.specroot=customRoot+"/specs/"+self.distro.name+"/"+self.version

        # convenience variable that olds extension to the proper module variant
        self.modext ='_'+self.distro.name
        self.modext+='_'+self.version
        self.modext+='_'+self.arch.name
        RimCore.rimcore.dbg(2, "        Amf Instance - %s%s", self.name, self.modext)
    
    def osKey(self):
        return self.modext
        
    def getRootPath(self):
        return self.rootPath
                            
#
# Component instance.
# the build environment is devied in the context of the product and node this
# component is being built for.
#
# A component like ha, for example, may be build multiple times and target
# nodes with vairous architecture of os release.
#
class CompInstance(RimCore.Variables):		
    appLibPath=[]
    #
    # Method to build a component of the application
    def __init__(self, comp, app, prod, svc, node, quiet=0):
        RimCore.rimcore.dbg(quiet, "                Reading Component - %s",comp.name)
        #
        # ready to build whatever it takes for a component.
        # We have the os/release/cpu combo so we can setup the tools.
        #
        # Build time variables for the associated application, service, product, 
        # and, finally, amf node variables are added to this context
        #
        self.env=self.copyEnvVars(node.env) 
        self.rim=node.rim
        self.env.compi=self
        self.addVars(app, self)
        self.addVars(comp, self)
        self.addVars(svc, self)
        self.addVars(prod, self)
        self.addVars(node, self)
        self.addVars(node.amfi, self)
        self.name=comp.name
        self.node=node
        self.app=app
        self.svc=svc
        self.prod=prod
        self.os=node.amfi.os.name
        self.distro=node.amfi.distro.name
        self.version=node.amfi.version
        self.cpu=node.amfi.arch.name
        self.env.amfi=node.amfi
        self.env.compi=self
        self.addVar("CPU", self.cpu)
        self.addVar("OSRELEASE",self.distro)
        self.addVar("COMPONENT", self.name)
        self.addVar("NODE", self.node.amfi.name)
        self.addVar("PRODUCT", self.prod.name)
        self.addVar("APPLICATION", self.app.name)
        self.objdir="%s_%s_%s" % (self.distro,self.version,self.cpu)
        self.rim.env['VDIR']=self.translate("%s" % self.objdir)
        self.env['OBJPREFIX']=self.translate("%s/" % self.objdir)
        self.env['VDIR']=self.translate("%s" % self.objdir)
        self.addVar("OBJDIR", self.objdir)
        self.rootRelDir="%s/%s/%s/%s" % (self.os,self.distro,self.version,self.cpu)
        self.rootPath="%s/%s" % (self.rim.rootsroot,self.rootRelDir)
        self.addVar("ROOT", self.rootPath)
        #
        # have rim also include the path to various libraries
        #
        target=self.rim.getOsArchTargetName(self.distro, self.version, self.cpu)
        Rim.addAppLibPaths(self, target, self.appLibPath)
        #
        # Ask rim for the tools PATH (path to compilers etc..) for this component
        toolsPath=node.prod.app.rim.getOsArchToolsPath(self.os, self.distro, self.version, self.cpu)
        
        # all tools scripts are under a specific directory relative
        # to $RIMROOT/scripts
        tpath="%s/crossTools/%s/%s/%s/%s" % (os.path.dirname(__file__), self.rim.hostTarget(), self.os,self.distro,self.cpu)
        f, filename, desc = imp.find_module('tools', [tpath])
        tools = imp.load_module('tools', f, filename, desc)
        
        tools.generate(self.env, toolsPath)
        try:
            self.env.MergeFlags({'LIBPATH' : [ self.rootPath+"/lib" ]})
            self.env.MergeFlags({'LIBPATH' : [ self.rootPath+"/usr/lib" ]})
            self.env.MergeFlags({'CPPPATH' : [ self.rootPath+"/usr/include" ]})
            if self.getVar("SPEC_ROOT") != "":
                self.rim.subdirs(self.translate("${SPEC_ROOT}/build"), self.env)
        except:
            None
        #
        # Record name of sconscript file at the root
        self.croot=comp.croot
        #
        # compute a full path stack for file searches
        #
        self.roots=[]
        #
        # Push a series of search paths used to search for spec elements and 
        # and implesite library depenedencies.
        #
        # Sequence would be something like:
        # /work/rim/custom/Linux/Ubuntu/lts10.4/x86_64
        # /work/rim/custom/Linux/Ubuntu/lts10.4
        # /work/rim/custom/Linux/Ubuntu/x86_64
        # /work/rim/custom/Linux/Ubuntu
        # /work/rim/custom/Linux/x86_64
        # /work/rim/custom/Linux
        # /opt/rimroots/Linux/Ubuntu/lts10.4/x86_64
        # /opt/rimroots/Linux/Ubuntu/lts10.4
        # /opt/rimroots/Linux/Ubuntu/x86_64
        # /opt/rimroots/Linux/Ubuntu
        # /opt/rimroots/Linux/x86_64
        # /opt/rimroots/Linux
        #
        self.pushTopOfRoot(self.rim.rootsroot)
        customRoot=self.rim.getVar("customRoot")
        self.pushTopOfRoot(customRoot)
        self.pushTopOfRoot(customRoot+'/common')
        self.pushTopOfRoot(customRoot+'/'+app.name)
        self.pushTopOfRoot(customRoot+'/'+prod.name)
        self.pushTopOfRoot(customRoot+'/'+node.amfi.name)
        self.pushTopOfRoot(customRoot+'/'+self.name)

    def pushTopOfRoot(self, root):
        self.roots.append("%s" % (root))
        root +='/'+self.os
        self.roots.append("%s" % (root))
        self.roots.append("%s/%s" % (root,self.cpu))
        self.roots.append("%s/%s/%s" % (root,self.distro,self.cpu))
        self.roots.append("%s/%s/%s" % (root,self.distro,self.version))
        self.roots.append("%s/%s/%s/%s" % (root,self.distro,self.version,self.cpu))
        
    def buildIt(self):
        sname=self.croot+'/rim.py'
        Rim.pushAppLibs(self.prod, self)
        Rim.pushAppLibs(self.app, self)
        Rim.pushAppLibs(self.svc, self)
        cRim=Rim.Rim(self.env, Rim.Rim.Shared)
        cRim.addVars(self, cRim);
        rpath=self.rootPath
        tname=self.node.amfi.distro.versions[self.version][self.cpu].tools
        #
        # have rim also include the path to various libraries
        #
        cRim.env['PREBUILTTARGET']=cRim.toolsets[tname].target
        cRim.addIncDirs( rpath+"/usr/include")
        cRim.addLibDirs( rpath+"/usr/lib")
        cRim.addLibDirs( rpath+"/lib")
        cRim.addLdFlags( "-Wl,-rpath-link=%s/lib" % rpath)
        cRim.addLdFlags( "-Wl,-rpath-link=%s/usr/lib" % rpath)
        myPath="/".join(os.path.realpath(__file__).split('/')[0:-2])
        cRim.env['ENV']['LD_LIBRARY_PATH']="%s/tools/lib" % myPath
        if self.cpu == 'x86_64':
            archDir="x86_64-linux-gnu"
            cRim.addIncDirs( rpath+"/usr/include/%s"%archDir)
            cRim.addLibDirs( rpath+"/usr/lib/%s"%archDir)
            cRim.addLibDirs( rpath+"/lib/%s"%archDir)
            cRim.addLdFlags( "-Wl,-rpath-link=%s/lib/%s" % (rpath,archDir))
            cRim.addLdFlags( "-Wl,-rpath-link=%s/usr/lib/%s" % (rpath,archDir))
        cRim.setApplicationName(self.app.name)
        cRim.setApplicationVersion(self.app.version)
        cRim.setProductName(self.prod.name)
        cRim.setComponentName(self.name)
        cRim.setOsBaseName(self.os)
        cRim.setOsReleaseName(self.distro)
        cRim.setCpuName(self.cpu)
        #
        # include a build of basic rim support lib
        #
        if os.access(sname, os.R_OK):
            cRim.subdirs(self.croot)
        else:
            RimCore.rimcore.dbg(1, "No rim.py file found in component root '%s'", self.croot);
        #
        # check for the presense of a spec file in the root/rim directory
        # We first look for a file with the component's name, then rim.spec
        #
        reqs=self.node.prod.stracker.processSpec(self.croot+'/rim', self.name, self, show=0)
        
        #
        # make sure we pick up all of the base OS modules for this component instance as well
        #
        for specfile in glob.glob(self.node.amfi.specroot+'/*.spec'):
            sname=os.path.basename(specfile)
            reqs+=self.node.prod.stracker.processSpec(self.node.amfi.specroot, sname[0:len(sname)-5], self, reqs)
        #    
        Rim.popAppLibs(self.svc, self)
        Rim.popAppLibs(self.app, self)
        Rim.popAppLibs(self.prod, self)

    def findFile(self, fname, defname, doFail=False, show=False, vdir=False):
        fpath=defname
        found=[]
        #
        # try all paths current in the roots[] array and return any 
        # existing match
        triggerFile="X/etc/shadow"
        if fname == triggerFile:
            RimCore.rimcore.dbg(0, "Searching for file '%s'...",fname)
            RimCore.rimcore.dbg(0, "Roots are '%s'..." % self.roots)
        for path in reversed(self.roots):
            fpath=path+"/"+fname
            if fname == triggerFile:
                print "Trying %s exists=%d" % (fpath, os.path.exists(fpath))
            if os.path.exists(fpath):
                RimCore.rimcore.dbg(8, "%s - Yes", fpath)
                found.append(fpath)
            else:
                RimCore.rimcore.dbg(8, "%s - No", fpath)
        #
        # check for a match in / only if the specified file is absolute
        # file source attribute starting with double slash are absolute
        #
        if fname[0:2] == "//" and os.path.exists(fname):
            RimCore.rimcore.dbg(8, "%s - Absolute", fname)
            found.append(fname)
        
        if len( found ):
            if show:
                print "Found file(s) : %s" % found
            return found
            
        # try adding the vdir 
        if not vdir:
            dir=os.path.dirname(fname)
            name=os.path.basename(fname)
            if dir == "":
                prefix=self.objdir
            else:
                prefix="%s/%s" % (dir, self.objdir)

            newfname="%s/%s" % (prefix, name)
            return self.findFile(newfname, defname, doFail, show, True)
            
        if show:
            print "Did not found file '%s' in any of :" % fname
            for path in self.roots:
                print "    %s" % path
            print "---> will return failure == %d" % doFail

        # If we are not alowed to fail...
        if not doFail:
            # if this is really not a test, return the last path tried.
            # this path shoudl be the one that points to the component
            # build root, so it will get proper handling from a build
            # dependancy.
            return [ fpath ]
        #
        # it is ok to fail and to use the default name supplied.
        return [ defname ]
        
    def findLib(self, libname, is64):
        for prefix in libPaths:
            archPrefixes=[ "", "/%s-linux-gnu" % self.cpu ]
            if self.cpu == "i686": archPrefixes += [ "32" ] 
            elif self.cpu == "x86_64": archPrefixes += [ "64" ] 
            for archPrefix in archPrefixes:
                paths=self.findFile("%s%s/%s"% (prefix,archPrefix,libname), 0, 1)
                if paths[0]:
                    return [ paths[0], prefix+'/'+libname ]
        return [ 0, 0 ]

class Service(RimCore.Variables):
    #
    # Method to build a component of the application
    def __init__(self, svcNode, app):
        self.env=self.copyEnvVars(app.env)
        self.comps={}
        self.xmlnode=svcNode
        self.name=svcNode.getAttribute('name')
        self.getVars(svcNode)
        compNodes=svcNode.getElementsByTagName('component')
        for comp in compNodes:
            cname=comp.getAttribute('name')
            if not app.components.has_key(cname):
                print "Invalid component name '%s' in service '%s'. '%s'" % (cname, self.name, svcNode.toxml())
                sys.exit(1)
            self.comps[cname]=app.components[cname]
    
class Node(RimCore.Variables):
    def __init__(self, amfNode, svcnames, app, prod, quiet=0):
        self.env=self.copyEnvVars(app.env)
        self.env=self.copyEnvVars(prod.env)
        #
        # Create an amf node instance that will help track everything
        # that's relevant for this amf-clm instance. (os + arch + os_version)
        self.amfi=AmfInstance(amfNode, prod.app.rim)
        self.amfi.product=prod
        self.compis={}
        self.prod=prod
        self.rim=prod.rim
        #
        # Extra optional prebuild lib paths
        Rim.getAppLibs(self, amfNode)
        #
        # before harvesting variables of that node 
        # inject those from all services is implements.
        #
        for svcname in svcnames:
            if prod.app.services.has_key(svcname):
                self.env=self.copyEnvVars(prod.app.services[svcname].env)
            else:
                print "Invalid service name '%s' in anf node '%s' - %s" % (svcname,self.amfi.name,amfNode.toxml())
                sys.exit(1)
        #
        self.getVars(amfNode)
        #
        # User can make build more focus (and thus fater) by specifying the 
        # Service and component he/she his working on
        #
        if os.environ.has_key('RIM_SERVICE'):
            thisService=os.environ['RIM_SERVICE']
        else:
            thisService=""
        if os.environ.has_key('RIM_COMPONENT'):
            thisComp=os.environ['RIM_COMPONENT']
        else:
            thisComp=""
        # 
        for svcname in svcnames:
            if thisService == "" or thisService==svcname:
                # Extra optional prebuild lib paths
                Rim.getAppLibs(self, app.services[svcname].xmlnode)
                Rim.pushAppLibs(prod, self)
                RimCore.rimcore.dbg(quiet, "            Reading Service - %s", svcname)
                svc=app.services[svcname]
                svcComps=svc.comps
                #
                # Find the component entry for this one.
                for comp in svcComps:
                    if thisComp == "" or thisComp==svcComps[comp].name:
                        self.compis[svcComps[comp].name]=CompInstance(svcComps[comp], app, prod, svc, self, quiet)
                Rim.popAppLibs(prod, self)
                
    def buildIt(self):
        print "        Node %s" % (self.amfi.name)
        for ckey in self.compis:
            print "            component %s" % (ckey)
            compi=self.compis[ckey]
            self.addVars(self, compi)
            compi.roots.append(compi.croot)
            compi.roots.append("%s/%s" %(compi.croot, compi.cpu))
            compi.buildIt()
            compi.roots.pop(0)
            compi.roots.pop(0)

class Product(RimCore.Variables):
    modEntries={}
    class modEntry:
        """
            This class will track the global module list which will be used
            for generating the bom in the final phase of the build
        """
        def __init__(self, mod):
            self.amfis={}
            self.variants={}
            self.digests={}
            self.mod=mod

    def __init__(self, prodNode, app, quiet=0):
        self.env=self.copyEnvVars(app.env)
        self.getVars(prodNode)
        self.nodes={}
        self.name=prodNode.getAttribute('name')
        self.revscs=prodNode.getAttribute('revScs')
        if self.revscs:
            import scsOps
            self.revision, self.view=app.rim.getScsRevAndView(self.revscs)
        else:
            self.revision="Unknown"
            self.view="Unknown"
        self.app=app
        self.desc=prodNode.getAttribute('desc')
        self.rim=app.rim
        self.rim.prod=self
        self.modules={}
        self.modEntries={}
        branch=os.getenv("RIM_BRANCH")
        workspace=os.getenv("RIM_WORKSPACE")
        self.repos="%s/%s/%s" % (workspace, branch, self.name)
        self.artifacts="%s/artifacts" % self.repos
        self.rim.env.app=app
        self.stracker=RimSpec.specTracker(self)

        # check is the user wants to build that node
        if os.environ.has_key('RIM_NODE') and os.environ['RIM_NODE'] != "":
            thisNode=os.environ['RIM_NODE']
        else:
            thisNode=0
        #
        # Extra optional prebuild lib paths
        Rim.getAppLibs(self, prodNode)
        
        amfNodes=prodNode.getElementsByTagName('amfNode')
        #
        # check for RIM_SET_ENV and warn user about missing node type
        #
        if thisNode == 0 and os.environ.has_key("RIM_SET_ENV"):
            print "Warning : To set the proper RIM environment you must"
            print "          specify the NODE for which you want to set the"
            print "          context for product '%s' and application '%s'" % (self.name, app.name)
            print "Available Nodes are: "
            for amfNode in amfNodes:
                nname=amfNode.getAttribute('name')
                print "     %s" % (nname)
            print "Please execute export RIM_NODE=<One of the Node Names listed Above>"
            sys.exit(1);

        for amfNode in amfNodes:
            nname=amfNode.getAttribute('name')
            # have to add the vars defined in the services this node participate in
            nodeServices=amfNode.getElementsByTagName('service')
            svcnames=[]
            for service in nodeServices:
                svcnames.append(service.getAttribute('name'))
            #
            # always add the basic rim service
            svcnames.append("Rim")
            for svcname in svcnames:
                self.addVars(app.services[svcname], self)
            if not thisNode or thisNode==nname:
                RimCore.rimcore.dbg(quiet, "        Node - %s",nname)
                self.nodes[nname]=Node(amfNode, svcnames, app, self, quiet)
                
    def buildIt(self):
        os.system("mkdir -p %s" % self.repos)
        #
        # Add the top level custom root for the APP 
        self.app.rim.roots.append(self.rim.getVar("customRoot")+"/"+self.app.name);
        
        #
        # push our parents custom libs
        Rim.pushAppLibs(self.app, self)
        
        # go through all nodes
        for nkey in self.nodes:
            self.addVars(self,self.nodes[nkey])
            customRoot=self.rim.getVar("customRoot")+"/"+self.app.name+"/"+nkey;
            self.app.rim.roots.insert(0,customRoot);
            self.nodes[nkey].buildIt()
            self.app.rim.roots.pop(0);
        
        # pop libs
        Rim.popAppLibs(self.app, self)
        # pop the App root
        self.app.rim.roots.pop(0);
            
                
    def addAmfiToModule(self, mod, amfi):
        if not self.modEntries.has_key(mod.name):
            self.modEntries[mod.name]=self.modEntry(mod)
        if not self.modEntries[mod.name].variants.has_key(amfi.modext):
            self.modEntries[mod.name].variants[amfi.modext]=mod
        if not self.modEntries[mod.name].amfis.has_key(amfi.name):
            self.modEntries[mod.name].amfis[amfi.name]=amfi

def printModule(cmd, target, source, env):
    return

class RimApp(RimCore.Variables):
    
    # list of all components for this app
    components={}
    # list of all services for this app
    services={}
    # List of modules that need to be gerenated for this app
    products={}
    
    def __init__(self, appNode, rim, quiet=0):
        self.appNode=appNode
        self.rim=rim
        rim.app=self
        self.env=self.copyEnvVars(rim.env)
        self.getVars(appNode)
        self.name=appNode.getAttribute('name')
        self.version=appNode.getAttribute('version')
        rim.pkgPrefix=appNode.getAttribute('pkgPrefix')
        if rim.pkgPrefix == "":
            rim.pkgPrefix=self.name
        self.tagSubStr=""
        #
        # Extra optional prebuild lib paths
        Rim.getAppLibs(self, appNode)
        #
        # build the component list
        #
        compRoot=appNode.getElementsByTagName('components')
        compNodes=compRoot[0].getElementsByTagName('component')
        for compNode in compNodes:
            comp=Component(compNode, self)
            if comp.root.scs in rim.branch.scs:
                comp.croot="%s/%s%s/%s" % (
                    rim.workspace, 
                    rim.scs[comp.root.scs].prefix, 
                    rim.branch.scs[comp.root.scs],
                    comp.root.prefix
                )
            else:
                comp.croot=""
            self.components[comp.name]=comp
        
        #
        # Add RIMROOT - for legacy references (need to clean these out)
        #
        self.rimroot=self.components['RimBase'].croot
        self.addVar("RIMROOT", "%s" % self.rimroot)
        self.rim.addVar("customRoot", "%s/custom" % self.rimroot)
        self.rim.addVar("RIMROOT", self.rimroot)
        #
        # Extract the service list
        #
        svcNodes=appNode.getElementsByTagName('services')[0].getElementsByTagName('service')
        for svcNode in svcNodes:
            self.services[svcNode.getAttribute('name')]=Service(svcNode, self);
            
        #
        # Extract the private keys
        #
        keyNodes=appNode.getElementsByTagName('key')
        self.keys={}
        for keyNode in keyNodes:
            self.keys[keyNode.getAttribute('name')]=keyNode.firstChild.wholeText
            
        #
        # Extract list of Products for this application
        # (or the one selected by the environment)
        #
        if os.environ.has_key('RIM_PRODUCT'):
            thisProd=os.environ['RIM_PRODUCT']
        else:
            thisProd=0
        prodNodes=appNode.getElementsByTagName('product')
        for prodNode in prodNodes:
            #
            # check for a match with user's environment
            # User could have no such environment which means all applications
            # shoudl be build.
            pname=prodNode.getAttribute('name')
            if not thisProd or thisProd==pname:
                RimCore.rimcore.dbg(quiet,"    Product - %s",pname)
                self.products[pname]=Product(prodNode, self, quiet)
                

    def getTagcodeDir(self):
        cdir="%s/%s/rimtag" % (self.rim.workspace, self.rimroot)
        print "tag cdor i s'%s'" % cdir
        return cdir
        
    def addSupportScripts(self, product):
        #
        # this is where we keep the list of the Rim support scripts or executables
        # that we which to include in the tarball 
        scripts="""
           doPostInstall
           installRim
           mountVersion
           rebuildRaid
           rimFuncs
           rimboot
           scratchInstall
           setUpDisk
           unMountVersion
        """.split()
        #
        # These can be changed based on Product or Application (for example)
        # so scan for them based on search path
        # define a few paths to look at based on product
        #
        #
        # define a few paths to look at based on product
        #
        roots=[]
        croot=self.rim.getVar("customRoot")
        roots.append("%s/%s/sbin" % (croot, product.name))
        roots.append("%s/%s/sbin" % (croot, self.name))
        roots.append("%s/common/sbin" % (croot))
        #
        # Add application list
        #
        appList=self.getVar("appTarFiles");
        if appList:
            scripts += appList.split();
        nodes=[]
        for script in scripts:
            path=None
            for r in roots:
                p="%s/%s" % (r, script)
                if os.path.exists(p):
                    path=p;
                    break;
            if not path:
                print "Path for support script %s not found, in any of :" % script
                for r in roots:
                    print "   %s/%s" % (croot, r)
                sys.exit(1);
            snode=self.rim.env.File(path)
            nodes.append(self.rim.env.Install(product.artifacts, snode) )
        return nodes

    def buildIt(self):
        #
        # we are done with the processing of the products
        # time to create all of the dependencies that will drive the build
        #
        class fileln:
            def __init__(self, path, mode="w"):
                self.f=open(path, mode)
                self.indent=0
            def push(self):
                self.indent+=4
            def pop(self):
                self.indent-=4
            def write(self, s):
                self.f.write("%s%s" % ("                "[0:self.indent], s))
                self.f.write('\n') 
            def close(self):
                self.f.close()
        def putBashList(f, name, sep, array):
            s="%s=(" % name
            for idx in range(0,len(array)):
                s+="'%s'" % array[idx]
                if idx == len(array)-1:
                    break;
                s+=sep
            s+=")"
            f.write(s);
        for prodKey in self.products:
            product=self.products[prodKey]
            #
            # first build that product
            #
            print "   Building dependencies for product %s" % prodKey
            self.addVars(self, product)
            product.buildIt()
            #
            # for all of the specs that we gathered for that product
            #
            defmod=[]
            modEntries=product.modEntries
            for modKey in modEntries:
                modEntry=modEntries[modKey]
                for varKey in modEntry.variants:
                    mod=modEntry.variants[varKey]
                    mod.addLibDeps()
                    defmod.append(mod.bnode)
                    if mod.bootable == "1":
                        os.system("mkdir -p %s" % product.artifacts)
                        fname=product.artifacts+"/vars.rim.sh"
                        f=fileln(fname)
                        for amfiKey in modEntry.amfis:
                            amfi=modEntry.amfis[amfiKey]
                            f.write("\nfunction %sVars()\n{" % (amfiKey))
                            f.push()
                            clm=amfi.clm
                            f.write("loaderType='%s'" % clm.loader)
                            f.write("preLoaderType='%s'" % clm.preloader)
                            #
                            # For each goes create a probe hook
                            f.write("function geoprobe()")
                            f.write("{")
                            #
                            f.push() 
                            for geo in clm.geonodes:
                                disk1=geo.disks.split(':')[0]
                                f.write("if [ -d /sys/block/%s ]" % disk1)
                                f.write("then")
                                f.push()
                                btpl=Template(geo.probe)
                                f.write("if (%s)" % btpl.substitute(devPath="/sys/block/%s" % disk1))
                                f.write("then")
                                f.push()
                                putBashList(f, "diskNames", " ", geo.disks.split(':'))
                                actualSizes=[]
                                for part in geo.parts.split(':'):
                                    if not len(part):
                                        actualSizes.append(part)
                                    elif part[-1] == 'G':
                                        actualSizes.append("%d" % (int(part[0:-1])*1024*1024))
                                    elif part[-1] == 'M':
                                        actualSizes.append("%d" % (int(part[0:-1])*1024))
                                    else:
                                        actualSizes.append(part)
                                putBashList(f, "partSizes", " ", actualSizes)
                                f.write('PLATFORM=%s' % geo.name)
                                for attr in vars(geo):
                                    f.write("%s='%s'" % (attr, getattr(geo,attr)))
                                f.write("return 0")
                                f.pop()
                                f.write("fi")
                                f.pop()
                                f.write("fi")
                            f.write("echo *******************************************************")
                            f.write("echo *")
                            f.write("echo *  Warning - Could not found valid disk device for")
                            f.write("echo *  node '%s' on this platform. Installation will" % amfiKey)
                            f.write("echo *  fail! Review Rim platofrm model to or fix this")
                            f.write("echo *  kernel!!")
                            f.write("echo *")
                            f.write("echo *******************************************************")
                            f.write("set -")
                            f.write("return 1")
                            f.pop()
                            f.write("}")
                            f.pop()
                            f.write("}")
                        f.close()
                        mod.addElement(fname, "/sbin/vars.rim.sh")
                            
                    if mod.knode: # check for a kernel to go along with this module.
                        defmod.append(mod.knode)
                    if mod.unode: # check for a loader to go along with this module.
                        defmod.append(mod.unode)
                    if mod.pnode: # check for a preloader to go along with this module.
                        defmod.append(mod.pnode)
                        
            #
            # create /sbin/vars.rim.sh addingvariables for each of the nodes via a node function
            #
            
            #
            # create the key files
            #
            for key in self.keys:
                open("%s/%s.prv_key" % (product.repos, key), "w").write(self.keys[key])
            #
            # Disabel printing of the builders target and sources
            #
            self.rim.env['PRINT_CMD_LINE_FUNC']=printModule
            #
            # create a dependancy for the bom
            #
            # Make sure we make the environment md5 vary based on revision number
            # Else the bom files will not get rebuild and tar, upd and iso will
            # have an invalide name
            #
            bNode1=self.rim.env.File(product.artifacts+"/bom.xml");
            bNode2=self.rim.env.File(product.artifacts+"/bom.sh");
            bNode3=self.rim.env.File(product.artifacts+"/vars.rim.sh");

            self.rim.setApplicationName(self.name)
            self.rim.setApplicationVersion(self.version)
            self.rim.setProductName(product.name)
            self.rim.env.prod=product
            tag=self.rim.getBldTag(product.repos)
            if os.environ.has_key('RIM_PACKAGES') :
                self.rim.env.Bom([ bNode1 ], defmod)
                tNode=self.rim.env.File("%s/%s.tgz" % (product.repos, tag))
                sNode=self.rim.env.File("%s/%s.upg" % (product.repos, tag))
                kNode=self.rim.env.File("%s/software.prv_key" % (product.repos))
                self.rim.env.TarBall([ tNode ] , [ bNode1, bNode2, bNode3 ] + defmod + self.addSupportScripts(product))
                self.rim.env.SignedUpg([ sNode ] , [ tNode, kNode ])
