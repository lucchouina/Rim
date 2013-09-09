from RimCore import *
import RimBuild
import RimUtils
from RimConf import *
import sys
import os 
import string
import xml.dom.minidom
import inspect
from string import Template

from SCons import Environment
from SCons import Script
from SCons import Node

# function to extract nodes from a single parent
def getChildrenByTagName(node, tagName):
    matches=[]
    for child in node.childNodes:
        if child.nodeType==child.ELEMENT_NODE and (child.tagName==tagName):
            matches.append(child)
    return matches
        
global bldTagVal;

class defaults:
    def getpath(self, key):
        return self.translate(self.node.getElementsByTagName(key)[0].getAttribute('path'))
    def readPaths(self, nodes):
        self.node=nodes[0]
        self.srcSubDir=self.getpath('srcSubDir')
        self.rootsRoot=self.getpath('rootsRoot')
        self.toolsRoot=self.getpath('toolsRoot')
        self.customRoot=self.getpath('customRoot')
        self.javaPath=self.getpath('javac')
        self.repos=self.getpath('repos')

class xmlToSconsEnv:

    sconsVarTab=[ 'LIBS', 'LIBPATH', 'CPPPATH', 'LINKFLAGS', 'CCFLAGS', 'CXXFLAGS' ]

    def setLibsAndFlags(self):
        # time to add any Node specific libraries 
        # they need to be at the end of the library list in the order
        # specified by the user
        for var in self.sconsVarTab:
            if self.getVar(var):
                v=self.translate(self.getVar(var))
                self.env.MergeFlags({var : v.split() })
        self.addLibs(self.envAppLibs)
        self.addLibDirs(self.envAppLibDirs)
        self.addLdFlags(self.envAppLdFlags)
        self.addIncDirs(self.envAppIncDirs)

    def resetLibs(self):
        for var in self.sconsVarTab:
            self.env[var]=[]

class Rim(RimCore.Variables, xmlToSconsEnv, RimConf):
    #
    Shared=1
    Private=0
    def __init__(self, penv=0, share=Private, showVars=0):
        if penv:
            if share==self.Shared:
                self.env=penv
            else:
                self.env=penv.Clone()
        else:
            # will allocate 'env'
            self.initVars()
            
            self.applibs=[]
            self.envAppLibs=[]
            self.envAppLibDirs=[]
            self.envAppIncDirs=[]
            self.envAppLdFlags=[]
        
        rev=os.getenv("revision")
        if not rev:
            rev="99999"
        self.setRevision(rev)
        #
        # check if  
        try:
            self.env.rim.translate("dummy")
            self.clmNodes=self.env.rim.clmNodes
            self.archNodes=self.env.rim.archNodes
            self.rimRoot=self.env.rim.rimRoot
            self.roots=self.env.rim.roots
            self.osNodes=self.env.rim.osNodes
            self.relNodes=self.env.rim.relNodes
            self.toolsets=self.env.rim.toolsets
        except:    
            if self.getVar("SPEC_ROOT") == None: self.addVar("SPEC_ROOT", "")
            RimConf.__init__(self)
            self.roots=[]
            self.env.rim=self # cross ref
            self.env.translate=self.translate
            self.env.Decider("MD5-timestamp");
            self.env.SConscriptChdir(0) # needed only so that the -j option will work
            self.applibs=[]
            self.envAppLibs=[]
            self.envAppLibDirs=[]
            self.envAppIncDirs=[]
            self.envAppLdFlags=[]
            #
            # register the builder for the bom and the modules with this env
            #
            RimBuild.registerBuilders(self.env)
    #
    # force an string arg to a list arg
    # and perform any required translations as well.
    #
    def toList(self, args, prefix="", suffix=""):
        if type(args) != type(list()):
            l=args.split()
        else:
            l=args
        l2=[]
        for e in l:
            l2.append("%s%s%s" % (prefix,e,suffix))
        return l2
    #
    # Include addition Variant directory into the mix
    #        
    def toListWithVdir(self, args, prefix="", suffix=""):
        if type(args) != type(list()):
            l=args.split()
        else:
            l=args
        l2=[]
        for e in l:
            l2.append("%s/%s" % (e, self.env['VDIR']))
            l2.append(e)
        return l2
            
    #
    # initialize a default set of Rim build environment variables
    def initEnv(self):
        pass
    
    # map variable uname[4] arch values to a single one 
    def archmap(self, arch):
        map={}
        map['armv5']='arm'
        map['i386']='i686'
        # add new types here
        if map.has_key(arch) :
            return map[arch]
        else :
            return arch
    # map variable uname[4] arch values to a single one 
    def archkmap(self, arch):
        map={}
        map['arm']='arm'
        map['i686']='x86'
        arch=self.archmap(arch)
        # add new types here
        if map.has_key(arch) :
            return map[arch]
        else :
            return arch
            
    def getTagcodeRoot(self):
        return self.rimtagRoot
    # To give some context to the rim files
    #
    def setApplicationName(self, name):
        self.env['APPLICATION']=name
    def setApplicationVersion(self, version):
        self.env['VERSION']=version
    def setProductName(self, name):
        self.env['PRODUCT']=name
    def setRevision(self, version):
        self.env['REV']=version
    def setComponentName(self, name):
        self.env['COMPONENT']=name
    def setOsBaseName(self, name):
        self.env['OSBASE']=name
        self.addVar("OSBASE", name)
    def setOsReleaseName(self, name):
        self.env['OSRELEASE']=name
    def setCpuName(self, name):
        self.env['CPU']=name
    def getApplicationName(self):
        return self.env['APPLICATION']
    def getRevision(self):
        return self.env['REV']
    def getApplicationVersion(self):
        return self.env['VERSION']
    def getProductName(self):
        return self.env['PRODUCT']
    def getComponentName(self):
        return self.env['COMPONENT']
    def getOsBaseName(self):
        return self.env['OSBASE']
    def getOsReleaseName(self):
        return self.env['OSRELEASE']
    def getCpuName(self):
        return self.env['CPU']
    #
    # compose a unique string for the host and arch
    def hostType(self):
        return os.uname()[0]+'_'+os.uname()[4]
    
    # used by product to query revision master scs
    def getScsRevAndView(self, scsName):
        for scs in self.scs:
            if scs==scsName:
                import scsOps
                scsop=scsOps.ScsOps(self.app, self.scs[scs])
                scsop.setDST(scsop.scsDstRoot())
                revision=scsop.Revision()
                view=scsop.View()
                if revision: return revision, view
                else: break
        return "Unknown", "Unknown"
    #
    # compose a unique string for the host and arch
    def hostTarget(self):
        osName=os.uname()[0]
        release=os.uname()[2]
        cpu=self.archmap(os.uname()[4])
        if osName == 'Linux':
            if cpu == 'i386':
                return 'i686-linux-gnu'
            else :
                return '%s-linux-gnu' % cpu
        elif osName == 'SunOS':
            if release == '5.10':
                suffix='solaris10'
            else:
                print "Release not supported '%s'" % release
                sys.exit(1)
            if cpu[0:3] == 'sun':
                return 'sparc-sun-%s' % suffix
        else:
            print "OS not supported '%s'" % release
            sys.exit(1)
    #
    # Return the tools name
    #
    def getOsArchToolsName(self, distro, version, cpu):
        return self.distros[distro].versions[version][cpu].tools
    #
    # Return the Target name
    #
    def getOsArchTargetName(self, distro, version, cpu):
        return self.toolsets[self.distros[distro].versions[version][cpu].tools].target
    #
    # Return the tools directory for a particular osRelease and arch
    #
    def getOsArchToolsPath(self, os, distro, version, cpu):
        relPath=self.getOsArchToolsName(distro, version, cpu)
        toolsCprefix=self.app.components['RimTools'].root.prefix;
        toolsVersion=self.branch.scs['tools']
        toolsRoot="%s/%stools_%s" % (self.workspace, toolsCprefix, toolsVersion)
        if relPath :
            return toolsRoot+"/"+self.hostType()+"/"+relPath
        else:
            return toolsRoot+"/"+self.hostType()+"/"+os+"/"+distro+"/"+cpu

    #
    # Makefiles hooks.
    #
    def subdirs(self, sdirs, e=None):
        if e:
            env=e;
        else:
            env=self.env.Clone()
        sdirs=self.toList(sdirs)
        for sdir in sdirs:
            sdir=self.translate(sdir)
            RimCore.rimcore.dbg(2,  "From %s, reading Rim.py file in '%s'.", self.myDir(), sdir+"/rim.py")
            if not os.path.exists(self.myDir()+'/'+sdir+"/rim.py"):
                if not os.path.exists(sdir+"/rim.py"):
                    if not env.has_key('QUIET') or not env['QUIET']:
                        print "Missing rim.py file @ %s" % sdir+"/rim.py"
                        self.bt()
                    return
            env.SConscript(sdir+"/rim.py", 'env')
        
    def hostEnv(self):
        env=Environment.Environment()
        env.vars={}
        return Rim(env)

    def useCxxforCFiles(self):
        self.env['CC']=self.env['CXX']
        self.env['SHCC']=self.env['SHCXX']

    def useCxxforLink(self):
        self.env['LINK']=self.env['CXX']

    # return the cross linking options 
    def xlinkOps(self):
        return [ ]

    # return the cross linking options 
    def xPath(self):
        try:
            return self.env['XPATH']
        except:
            return '/'

    # return the cross linking options 
    def osBase(self):
        try:
            return self.env['OSBASE']
        except:
            return 'unknown'

    #  debug
    def pkey(self, key, prefix=""):
        if self.env.has_key(key):
            print prefix+" - key '"+key+"' exist == "+self.env[key]
        else:
            print prefix+" - key '"+key+"' Unknown"
        
    def useCcforCFiles(self):
        self.env['CC']='gcc'
        
    def setObjSuffix(self, s):
        self.env['OBJSUFFIX']=s

    def command(self, s):
        RimCore.rimcore.dbg(1, "Rim command '%s'", s)
        return os.system(s)

    def srcList(self):
        sdir="%s/src" % self.myDir()
        if os.path.isdir(sdir):
            dir=sdir
        else:
            dir=self.myDir()
        srcList=self.env.Glob(dir+"/*.[cly]", source=True)
        return srcList

    def srcFromDir(self, dir, src, prefix="", postfix=""):
        flist=[]
        for file in src:
            flist.append(dir+'/'+prefix+file+postfix)
        return flist
    #
    # variable substitution on a list of paths
    #
    def swapVars(self, paths):
        npaths=[]
        for path in paths:
            tpath=self.translate(path)
            if not tpath in npaths:
                npaths.append(self.translate(path));
        return npaths

    #
    # Give a way for components to add libraries to their link phase
    # and to add library directory too.
    #
    def addLibs(self, libList, replace=0):
        libList=self.toList(libList)
        if not replace:
            self.env.MergeFlags({'LIBS' : libList })
        else:
            self.env['LIBS']=libList

    def addLibDirs(self, dirList, replace=0):
        dirList=self.toListWithVdir(dirList)
        ndirList=self.swapVars(dirList)
        self.env.MergeFlags({'LIBPATH' : ndirList })

    def addLdFlags(self, flagList):
        flagList=self.toList(flagList)
        self.env.MergeFlags({'LINKFLAGS' : flagList })

    def addIncDirs(self, dirList, root=None):
        dirList=self.toList(self.translate(dirList))
        if root:
            for dir in dirList:
                dirList[dir]="%/%s" (root, dirList[dir])
        ndirList=self.swapVars(dirList)
        self.env.MergeFlags({'CPPPATH' : ndirList })

    def prependIncDirs(self, dirList, root=None):
        dirList=self.toList(self.translate(dirList))
        if root:
            for dir in dirList:
                dirList[dir]="%/%s" (root, dirList[dir])
        ndirList=self.swapVars(dirList)
        for d in ndirList:
            self.env.Prepend(CPPPATH = d)        

    #
    # storage functions for appLibs environment which needs to be pushes 
    # at the end of the final environment instead of where they appear in 
    # in the script
    #
    def addAppLibDirs(self, dirList):
        self.envAppLibDirs.extend(self.toList(dirList))

    def addEnvAppLibs(self, libList):
        self.envAppLibs.extend(self.toList(libList))

    def addAppIncDirs(self, dirList):
        self.envAppIncDirs.extend(self.toList(dirList))

    def addAppLdFlags(self, flagList):
        self.envAppLdFlags.extend(self.toList(flagList))

    def addCppFlags(self, flagList, replace=0):
        flagList=self.toList(self.translate(flagList))
        if not replace:
            self.env.MergeFlags({'CCFLAGS' : flagList })
        else:
            self.env['CCFLAGS']=flagList
    
    def addCflags(self, flagList, replace=0):
        self.addCppFlags(flagList, replace)

    def addCxxFlags(self, flagList, replace=0):
        flagList=self.toList(self.translate(flagList))
        if not replace:
            self.env.MergeFlags({'CXXFLAGS' : flagList })
        else:
            self.env['CXXFLAGS']=flagList
    #
    # reset all flags to nothing (use for .o build)
    # This is so that we have a single rimtag.o for each target
    #
    def rstCcFlags(self):
        self.env['CXXFLAGS']=[]
        self.env['CCFLAGS']=[]        
        self.env['CFLAGS']=[]        
        self.env['LIBPATH']=[]
        self.env['CPPPATH']=[]
        self.env['LINKFLAGS']=[]
        self.env['CPPFLAGS']=[]
        self.env['_CPPDEFFLAGS']=[]
        self.env['_CPPINCFLAGS']=[]
    
    def myDir(self):
        return self.env.Dir('.').abspath
        
    #
    # BUILD naming functions. Tags and build number
    # The builder can oveeride the derived build tag which is a composite of the
    # product and application names.
    #
    def buildNumber(self, repo, inc=0):
        cfname="%s/bldCount.txt" % (repo)
        try:
            cfile=open(cfname, "r")
            cstr=cfile.read()
            count=string.atoi(cstr, 10)
            cfile.close()
        except:
            count=0
        
        # increment the counter if 
        if inc == 1:
            count=count+1
            cfile=open(cfname, "w")
            rs="%03d\n" % (count)
            cfile.write(rs)
            cfile.close();
        return "%03d" % (count)
        
    def incBuildNumber(self, repo):
        return self.buildNumber(repo, inc=1)
    
    #
    # Create a unique build tag
    #
    # We cascade the formats in order of the numbew of arguments.
    # python will thow an exception until we hit on the right number of them.
    #                      
    def getBldTag(self, repo):
        self.getRevision()
        # builder can override via environment
        if os.environ.has_key('BLD_TAG'):
            bldTag=os.environ['BLD_TAG'];
        else:
            bldTag="${COMPANY}-${PRODUCT}-${VERSION}-${NUMBER}"
        
        btpl=Template(bldTag)
        try:
            return btpl.substitute(
                COMPANY=self.getApplicationName(),
                PRODUCT=self.getProductName(),
                VERSION=self.getApplicationVersion(),
                NUMBER=self.buildNumber(repo, 0)
            )
        except:
            raise
            print "Invalid BLD_TAG value - '%s'" % bldTag
            print "Available variables are : "
            print "    COMPANY  - Company wide identifier - example: 'S2'"
            print "    PRODUCT  - Target Product name - example: 'Global'"
            print "    VERSION  - Software version - example: '1.1.02'"
            print "    NUMBER   - Build number - example: '12'"
            sys.exit(1)

    def vName(self, name):
        return "%s/%s" % (self.env['VDIR'], name)

    # Libraries and program creation functions
    # Use either all of the sources inside the 'src' subdir or
    # the specified list of source files.
    #
    def Lib(self, isShared, name, src):
        if isShared:
            self.env.SharedLibrary(self.vName(name), src)
        else:
            self.env.StaticLibrary(self.vName(name), src)

    def Objects(self, src):
        self.setLibsAndFlags()
        return self.env.StaticObject(src);

    def objVariant(self, objs, dir=None):
        l=[]
        for o in objs:
            no="%s%s%s" % (self.env['OBJPREFIX'], o, self.env['OBJSUFFIX'])
            if dir:
                l.append("%s/%s" % (dir, no))
            else:
                l.append(no)
        return l;

    def Nodes(self, src):
        return self.env.Node(src);

    def SharedObjects(self, src):
        self.setLibsAndFlags()
        return self.env.SharedObject(src);

    def SharedLib(self, name, src=None):
        if not src: src=self.srcList()
        self.setLibsAndFlags()
        return self.Lib(1, name, src)

    def StaticLib(self, name, src=None):
        if not src: 
            src=self.srcList()
        self.setLibsAndFlags()
        return self.Lib(0, name, src)

    def Program(self, name, src=None):
        if not src: src=self.srcList()
        self.setLibsAndFlags()
        return self.env.Program(self.vName(name), src);
    #
    # to create a host based program, user calls this function
    # followed by HostProgram() to bypass lib setup
    #
    def HostEnv(self):
        self.resetLibs();
        
    def HostProgram(self, name, src=[]):
        if not src: src=self.srcList()
        return self.env.Program(self.vName(name), src);
        
    def TaggedProgram(self, name, src=[]):
        if not src: src=self.srcList()
        # add the tag source file to it and use default compile options
        self.addIncDirs([ self.translate(self.getTagcodeRoot()) ])
        self.setLibsAndFlags()
        self.env.TaggedProg(self.vName(name), self.vName(name+".unt"));
        self.addLibs("rim");
        self.addLibDirs(self.translate(self.getTagcodeRoot()))
        return self.Program(name+".unt", src);
        
    def Java(self, classDir, srcDir):
        return self.env.Java(classDir, srcDir, JAVAVERSION='1.5');
        
    def Jar(self, jarName, classDir):
        return self.env.Jar(jarName, classDir);
    
        
    #
    # Add a pre-build lib to an environment
    #
    def addAppLibs(self, liblist, runList=[]):
        liblist=self.toList(liblist)
        # user supplies a list of library he wishes to use
        for lib in liblist:
            # each applibs entry is a full blown AllLib object
            found=0;
            #prtLibs(self);
            print "661 self=%s" % self
            print "662 env=%s" % self.env
            for glib in self.env.applibs:
                match=glib.findMatch(lib)
                if match:
                    libPath=glib.root+'/'+self.env['PREBUILTTARGET']+'/'+match.fname
                    if os.access(libPath, os.R_OK):
                        self.addAppLibEnvSet(match, libPath, [ match.alias() ])
                        found=1
                        break;
                    else:
                        print "Could not access lib path '%s'" % libPath
            if not found:
                print "Warning: could not find library/alias '%s'" % lib
                self.bt(100);
                os.sys.exit(1)
    #
    # Prep the environment based on the appLib 
    #
    def addAppLibEnvSet(self, match, libPath, runList):
        self.addAppLibDirs(libPath)
        self.addAppIncDirs(libPath)
        # any other sub directories that need to be explicitely included
        # have been specified with -I options in the aliases file.
        for incDir in match.incDirs:
            self.addAppIncDirs(libPath+"/"+incDir)
        self.addEnvAppLibs(match.alias())
        #
        # recursively include any explicite dependencies from that 
        # libary to others and on.
        #
        self.addAppLibDepends(match, runList);
        
    #
    # scan trough library dependencies (for app Libs)
    # and insert them. Follow a cal to the addAppLibs() call above.
    # For example, if libcurl is built with libldap support we, need to add
    # libldap to the link phase.
    #
    def addAppLibDepends(self, match, runList):
        #
        # depends[] contains the list of dependencirs.
        # it is also a list of libraries 
        for dep in match.depends:
            found=0
            for glib in self.env.applibs:
                dmatch=glib.findMatch(dep)
                if dmatch:
                    found=1
                    if not dmatch.alias() in runList:
                        runList.append(dmatch.alias())
                        self.addAppLibs(dep, runList)
            if not found:
                print "Missing dependency '%s' on lib '%s'" % (dep, match.alias())
                os.sys.exit(1);
            
#
# for any given nodes of the Application XML, use gets oppportunity 
# to change link and compile flags.
#
def getAppLibs(this, node):
    this.env.applibs=[]
    prenodes=node.getElementsByTagName('preBuild')
    for prenode in prenodes:
        path=this.translate(prenode.getAttribute('path'))
        this.env.applibs.append(AppLib(path))

#
# Add search paths for the defined app libs 
#
def addAppLibPaths(this, prefix, paths):
    for glib in this.env.applibs:
        glib.addPaths(prefix, paths)
#
# print my list
def prtLibs(this):
    for path in this.env.applibs:
        path.prt()
#
# Add a parent's applibs to ours
#
def pushAppLibs(parent, me):
    for path in parent.env.applibs:
        me.env.applibs.append(path)
        
def popAppLibs(parent, me):
    for path in parent.env.applibs:
        me.env.applibs.pop()
#
# use this for tagging purposes.
# Scons will complain if different environments try to put the same object in the tree.
#
global tagrim
env=Environment.Environment()
env.vars={}
tagrim=Rim(env);
tagrim.useCxxforCFiles()

class AppLib:
    class agroup:
        def __init__(self, fullname, tokens):
            self.subs=[]
            self.incDirs=[]
            self.aliases=[]
            self.depends=[]
            self.fname=fullname
            for idx in range(1,len(tokens)):
                # a sub lib?
                if tokens[idx][0:1]=='+':
                    self.subs.append(tokens[idx][1:])
                elif tokens[idx][0:1]=='@':
                    self.depends.append(tokens[idx][1:])
                elif tokens[idx][0:2]=='-I':
                    self.incDirs.append(tokens[idx][2:])
                else:
                    self.aliases.append(tokens[idx])
        def hasSub(self, fullname):
            if fullname in self.subs:
                return 1;
            else:
                return 0;
        def fullname(self):
            return self.fname
        def alias(self):
            return self.aliases[0]
            

    def __init__(self, root):
        self.root=root;
        self.agroups={}
        self.subs=[]
        if os.access(root+"/aliases", os.R_OK):
            afile=open(root+"/aliases");
            line=afile.readline()
            lineno=1
            while line:
                line=afile.readline()
                tokens=line.strip().split(':')
                if tokens[0][0:1]=='#':
                    continue;
                fullname=tokens[0]
                #
                # check if any of the aliases we already have 
                # has this one as a sub
                #
                isSub=0
                for agKey in self.agroups:
                    ag=self.agroups[agKey]
                    if ag.hasSub(fullname):
                        # use this ones fullname
                        isSub=1
                        self.agroups[fullname]=self.agroup(ag.fname, tokens)
                        break
                if not isSub:
                    self.agroups[fullname]=self.agroup(tokens[0], tokens)
                lineno=lineno+1
            afile.close();
        else:
            print "Warning : Cannot access alias file for root '%s'" % root
    #
    # find a match to a fulnname or an alias
    #
    def findMatch(self, lib):
        for agKey in self.agroups:
            ag=self.agroups[agKey]
            if ag.fname == lib:
                return ag
            for alias in ag.aliases:
                if alias == lib:
                    return ag
        return None
    #
    # Add the paths to all defined libs to an array of search paths
    #
    def addPaths(self, prefix, paths):
        if prefix:
            path="%s/%s" % (self.root, prefix)
        else:
            path=self.root
        for agKey in self.agroups:
            p="%s/%s" % (path, self.agroups[agKey].fname)
            if p not in paths:
                #print "Adding lib path %s" % p
                paths.append(p)
    #
    # print it
    def prt(self):
        for agKey in self.agroups:
            ag=self.agroups[agKey]
            print "Name - %s" % ag.fname
            for alias in ag.aliases:
                print "    Alias - %s" % alias
