import sys, os, shutil, traceback, fcntl, time, subprocess
import stat as myStat
import string
import time
from string import Template
from SCons import Builder
import RimUtils
import RimCore

class modClass:

    actions={}
    
    def __init__(self, target, source, env):
    
        # create a file to log module file provenance
        dir=os.path.dirname(target[0].abspath);
        top=os.path.dirname(dir)
        fname=os.path.basename(target[0].abspath);
        self.lfd=open("%s/logs/%s.flist" % (top,fname), "w");

        self.env=env.Clone()
        self.actions['dir']=self.buildDir
        self.actions['emptydir']=self.buildDir
        self.actions['emptyfile']=self.buildEmptyFile
        self.actions['link']=self.buildLink
        self.actions['node']=self.buildNode
        self.actions['file']=self.buildFile
        self.mod=env.module
        RimCore.rimcore.dbg(2, "Building module - %s",self.mod.name)
        # create a temp root, where to put the files
        self.root="%s/%s.root" % (top, self.mod.name)
        os.system("/bin/rm -rf "+self.root)
        os.mkdir(self.root,0755)
        self.target=target
        self.source=source
        #
        # create a pipe to which we can send some commands
        # this pipe might implement the fakeroot function so that
        # any user can create nodefiles and other items without
        # needed a setuid program
        #        
        (self.fake_rfd, self.fake_wfd) = os.pipe()
        (self.bash_rfd, self.bash_wfd) = os.pipe()
        #
        # uncomment below to turn on verbose output of the build fakeroot bash process
        #
        #os.write(self.bash_wfd, "set -vx\n")
        fcntl.fcntl(self.fake_wfd, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(self.fake_rfd, fcntl.F_SETFL, os.O_NONBLOCK)
        if os.environ.has_key('FAKEROOTKEY'):
            del os.environ['FAKEROOTKEY']
        if os.environ.has_key('LD_PRELOAD'):
            del os.environ['LD_PRELOAD']
        self.fakePipe=subprocess.Popen("faked --foreground", bufsize=0, shell=True, stdout=self.fake_wfd);
        time.sleep(1)
        fakeKey=os.read(self.fake_rfd, 100)
        os.environ['LD_LIBRARY_PATH']=os.environ['LD_LIBRARY_PATH']+':'+self.env.rim.translate("${RIM_WORKSPACE}/lib")
        os.environ['FAKEROOTKEY']=fakeKey
        os.environ['LD_PRELOAD']="libfakeroot.so"
        os.environ['FS_ROOT']=self.root
        os.environ['FS_NAME']=self.target[0].abspath
        self.bashPipe=subprocess.Popen("bash", bufsize=0, shell=True, stdin=self.bash_rfd);
        
    def closeAll(self):
        os.write(self.bash_wfd, "exit\n")
        self.lfd.close();
        os.close(self.bash_rfd);
        os.close(self.bash_wfd);
        os.close(self.fake_rfd);
        os.close(self.fake_wfd);
        retCode=self.bashPipe.wait()
        self.fakePipe
        if retCode:
            print "Error with bash exit [%d]" % (retCode)
       
    def bashWrite(self, s):
        os.write(self.bash_wfd, s)
        os.flush(self.bash_wfd)
    
    def buildIt(self):
    
        try:
            for ekey in self.mod.elements:
                elem=self.mod.elements[ekey]
                self.actions[elem.type](elem);
            #
            # We are done creating the files
            # Call OS specific fs builder to create the module
            #print "Root is : " + self.root
            #os.system("bash");
            os.write(self.bash_wfd, self.env.amfi.os.fsbuilders[self.mod.fstype])

        except Exception, details:
            print "Failed creation of module "+self.mod.name
            print details
            print "Stack back trace :"
            print "------------------------------"
            traceback.print_exc()
            print "------------------------------"
            os.environ['LD_PRELOAD']=""
            self.closeAll()
            os.system("/bin/rm -rf "+self.root)
            os.kill(self.fakePipe.pid, 15)
            time.sleep(1)
            os.kill(self.fakePipe.pid, 9)
            os.environ['FAKEROOTKEY']=''
            return 1
            
        os.environ['LD_PRELOAD']=""
        self.closeAll()
        os.system("/bin/rm -rf "+self.root)
        os.system("killall faked")
        #os.system("pkill -TERM -P%d" % self.fakePipe.pid)
        #os.system("kill -TERM %d" % self.fakePipe.pid)
        time.sleep(1)
        #os.system("pkill -KILL -P%d" % self.fakePipe.pid)
        #os.system("kill -KILL %d" % self.fakePipe.pid)
        os.environ['FAKEROOTKEY']=''
        return 0

    # recurse creating directories leading to a file/dir
    def buildDirs(self, dname):
        if len(dname) < 3:
            return
        self.lfd.write("[Dir ] %s \n" % (dname))
        self.buildDirs(os.path.dirname(dname))
        try:
            os.mkdir(self.root+dname, 0755)
        except:
            return

    # directory
    def buildDir(self, elem):
        tdir=elem.target
        if elem.show == "1":
            print "install -d -g%s -o%s -m%s '%s'\n" % (elem.group, elem.owner, elem.perms, self.root+elem.target)
            
        #print "install -d -g%s -o%s -m%s '%s'\n" % (elem.group, elem.owner, elem.perms, self.root+elem.target)
        os.write(self.bash_wfd, "install -d -g%s -o%s -m%s '%s'\n" % (elem.group, elem.owner, elem.perms, self.root+elem.target))
        #self.buildDirs(tdir)

    # symbolic name
    def buildLink(self, elem):
        try:
            self.lfd.write("[link] %s -> %s\n" % (elem.source, elem.target))
        except:
            return
        tdir=os.path.dirname(elem.target)
        self.buildDirs(tdir)
        symtarget = self.root+elem.target
        try:
            if os.path.exists(symtarget):
              if not os.path.samefile(elem.source, symtarget):
                os.remove(symtarget)
            if not os.path.exists(symtarget):
              os.symlink(elem.source, symtarget)
        except:
            print "Failed to create link %s -> %s" % (elem.source, symtarget)

    # node file
    def buildNode(self, elem):
        self.lfd.write("[node] %s type=%s major=%s, minor=%s\n" % (elem.target, elem.nodetype, elem.major, elem.minor))
        tdir=os.path.dirname(elem.target)
        self.buildDirs(tdir)
        os.write(self.bash_wfd, "mknod %s %s %s %s\n" % 
            (self.root+elem.target,
            elem.nodetype,
            elem.major, elem.minor));

    # empty file
    def buildEmptyFile(self, elem):
        self.lfd.write("[EmptyFile] %s type=%s major=%s, minor=%s\n" % (elem.target, elem.nodetype, elem.major, elem.minor))
        tdir=os.path.dirname(elem.target)
        self.buildDirs(tdir)
        os.write(self.bash_wfd, "install -g%s -o%s -m%s /dev/null '%s'\n" % (elem.group, elem.owner, elem.perms, self.root+elem.target))

    # file
    def buildFile(self, elem):
        tdir=os.path.dirname(elem.target)
        #print "target is %s" % elem.target
        self.lfd.write("[file] %s -> %s\n" % (elem.path, elem.target))
        self.buildDirs(tdir)
        # print "File '%s' perms '%s' path='%s'\n" % (elem.path, elem.perms, self.root+tdir)
        # make sure the source is actually a file
        if not os.path.isfile(elem.path):
            print "File item source is not a file'"+elem.source+"'"
            sys.exit(1)

        # optimize by using hard links for same device        
        cmd="install -g%s -o%s -m%s '%s' '%s'\n" % (elem.group, elem.owner, elem.perms, elem.path, self.root+elem.target)
        #print cmd
        os.write(self.bash_wfd, cmd)
        #os.write(self.bash_wfd, "cp %s %s\n" % (elem.path, self.root+elem.target))
        #os.write(self.bash_wfd, "chown %s:%s %s\n" % (elem.owner, elem.group, self.root+elem.target))
        #os.write(self.bash_wfd, "chmod %s %s\n" % (elem.perms, self.root+elem.target))
        #shutil.copy(elem.path, self.root+elem.target)
        #os.chmod(self.root+elem.target, string.atoi(elem.perms, base=8))
        #os.chown(self.root+elem.target, string.atoi(elem.owner), string.atoi(elem.group))
    
    
def buildModule(target, source, env):
    print "Building module: %s" % ( target[0].abspath )
    mc=modClass(target, source, env)
    mc.buildIt()

# put together a bill of material file for a specific product
def buildBom(target, source, env):

    print "Building Final BOM: %s" % ( target[0].abspath )
    dirUp=os.path.dirname(os.path.dirname(target[0].abspath))
    # Produce the various context scripts for that module
    # global variables cover Product, Application 
    def scriptGlobals(env, pkgname):
        shfile.write("rimApplication=\"%s\"" % env.rim.app.name)
        shfile.write("rimApplicationVersion=\"%s\"" % env.rim.app.version)
        shfile.write("rimBuildNumber=\"%s\"" % env.rim.buildNumber(dirUp))
        shfile.write("rimProduct=\"%s\"" % env.rim.prod.name)
        shfile.write("rimPrivSoft=\"soft/%s\"" % pkgname)
        shfile.write("rimPubSoft=\"soft\"")
        shfile.write("rimPrivData=\"data/%s\"" % pkgname)
        shfile.write("rimPubData=\"data\"")
        shfile.write("rimPivot=\"pivot\"")
        
    # toput a list assignment for bash with spaces or something else.
    def putBashList(shfile, name, sep, array):
        s="%s=(" % name
        for idx in range(0,len(array)):
            s+="%s" % array[idx]
            if idx == len(array)-1:
                break;
            s+=sep
        s+=")"
        shfile.write(s);
                
    #
    # node specific variables
    #
    def scriptNodeSpecific(amfi):
        shfile.write("    rimNode=\"%s\"" % amfi.name)
        shfile.write("    rimOs=\"%s\"" % amfi.os.name)
        shfile.write("    rimRelease=\"%s\"" % amfi.os.name)
        shfile.write("    rimReleaseVersion=\"%s\"" % amfi.version)
        amfi.varsToFile(shfile, "    ");
        
    class fileln:
        def __init__(self, path, mode):
            self.f=open(path, mode)
        def write(self, s):
            self.f.write(s)
            self.f.write('\n') 
        def close(self):
            self.f.close()
    pkgname=env.rim.getBldTag(dirUp)
    lut={}
    lut['rimBuildLabel']=pkgname
    lut['rimBuildUser']=os.environ["USER"]
    lut['rimBuildTime']=os.popen("date","r").readline().rstrip()
    lut['rimBuildView']=env.prod.view
    lut['rimBuildRev']=env.prod.revision
   
    xmlfile=fileln(target[0].abspath, 'w')
    shfile=fileln(target[0].abspath[0:-4]+".sh", 'w')
    varfile=open(target[0].abspath[0:-4]+".py", 'w')
    xmlfile.write("<?xml version='1.0' ?>")
    xmlfile.write('<bom version="1.0">')
    shfile.write("#\n# This is a copy of the Bom .xml file suitable for consumption in scripts\n#\n\n")
    for varname in sorted(lut):
        if os.environ.has_key(lut[varname]):
            envval=os.environ[lut[varname]]
        else:
            envval=lut[varname]
            
        xmlfile.write('    <%-12s value="%s"/>' % (varname, envval))
        shfile.write('%s="%s"' % (varname, envval))
    
    shfile.write("[ -f /sbin/vars.rim.sh ] && . /sbin/vars.rim.sh")
    shfile.write("[ -f ./vars.rim.sh ] && . ./vars.rim.sh")
       
    #
    # insert below any RIm specific actions that will set variables for the rest of the 
    # scripts.
    #
    #shfile.write("%s" % """
    #            #
    #            # The two next line will initialize the platform and disks
    #            
    #            if [ -f /sbin/rimFuncs ]
    #            then
    #                . /sbin/rimFuncs
    #                getDiskNames
    #            fi
    #""")
    
    # insert the list of modules and amf nodes
    # this is with the modules name only, no arch and os release and version
    # The actual module file selection will be done at run time
    # using the AMF to CLM map information
    
    #
    # Create a set of scripts, one for each context
    # 1 - post-install  (after install)
    # 2 - pre-reboot    (prior to reboot after install)
    # 3 - first-boot    (first boot after install)
    # 4 - up            (normal boot up)
    # 5 - down          (normal shutdown)
    #
    
    #
    # First pass for xml version
    #
    modEntries=env.prod.modEntries
    for modKey in modEntries:
        modEntry=modEntries[modKey]
        modEntry.skip=False
        module=modEntry.mod
        s='    <module name="%s" ' % (module.name)
        s+='version="%s" ' % (module.version)
        s+='required="%s" ' % (module.isRequired)
        s+='level="%s" ' % (module.level)
        s+='bootable="%s">' % (module.bootable)
        xmlfile.write(s)	
        for amfiKey in modEntry.amfis:
            amfi=modEntry.amfis[amfiKey]
            xmlfile.write('        <amf name="%s"/>' % (amfi.name))
        for varKey in modEntry.variants:
            mod=modEntry.variants[varKey]
            vname=mod.bnode[0].abspath
            modEntry.digests[varKey]=RimCore.rimcore.fileDigest(vname, 100000)
            xmlfile.write('        <variant name="%s" md5="%s"/>' % (varKey[1:], modEntry.digests[varKey]))
        xmlfile.write('    </module>')
    xmlfile.write('</bom>')
    #
    # Second pass for sourceable shell version
    #
    scriptGlobals(env, pkgname)
    amfEntries=env.prod.nodes;
    nodeList=[]
    for nodeName in amfEntries:
        shfile.write("\nfunction %s()\n{" % (nodeName));
        clm=amfEntries[nodeName].amfi.clm
        # source from the variables for that node created by RmApp.py
        shfile.write("    %sVars" % nodeName)
        shfile.write("    geoprobe")
        nodeList += [ nodeName ];
        modEntries=env.prod.modEntries
        scripts={}
        modlist={}
        modIndex=0
        scriptSpecDone=False
        variant=""
        for modKey in modEntries:
            modEntry=modEntries[modKey]
            mod=modEntry.mod
            for varKey in modEntry.variants:
                for amfiKey in modEntry.amfis:
                    amfi=modEntry.amfis[amfiKey]
                    if amfi.name == nodeName and amfi.modext == varKey:
                        variant=varKey
                        if not scriptSpecDone:
                            scriptNodeSpecific(amfi)
                            scriptSpecDone=True
                        #
                        # if this module has an entry for this amfNode record it.
                        shfile.write("    module[%d]=%s" % (modIndex, mod.name))
                        shfile.write("    md5[%d]=%s" % (modIndex, modEntry.digests[varKey]))
                        shfile.write("    level[%d]=%s" % (modIndex, mod.level))
                        for script in mod.scriptText:
                            if not scripts.has_key(script) :
                                scripts[script]={}
                                modlist[script]={}
                            slist=scripts[script]
                            rank=mod.scriptRank[script]
                            if slist.has_key(rank):
                                if mod.name != modlist[script][rank]:
                                    print "Duplicate ranking %s for script '%s'" % (rank, script)
                                    print "    module %s and module %s" % (mod.name, modlist[script][rank])
                                    print [ r for r in sorted(modlist[script])]
                                    sys.exit(1)
                            else:
                                slist[rank]=mod
                                modlist[script][rank]=mod.name
                        modIndex+=1
        for context in scripts:
            shfile.write("    function %s()    {" % context)
            for rank in sorted(scripts[context]):
                mod=scripts[context][rank]
                shfile.write("        #"); 
                shfile.write("        # %s commands for module %s - rank %s" % (context, modlist[context][rank], rank)); 
                shfile.write("        #"); 
                shfile.write("        function %s_%s()    {\n" % (modlist[context][rank], rank));
                mod.varsToFile(shfile, "            ")
                shfile.write("            rimModule=\"%s\"" % mod.name)
                shfile.write("            rimModuleVersion=\"%s\"" % mod.version)
                shfile.write("%s" % mod.scriptText[context])
                shfile.write("        }\n")
            shfile.write("        #\n        # Call these functions in order of their rank.\n        #");
            for rank in sorted(scripts[context]):
                #shfile.write("        echo '      %s' 1>&2" % (modlist[context][rank]));
                shfile.write("        %s_%s $* || return 1" % (modlist[context][rank], rank));
            shfile.write("        return 0");
            shfile.write("    }")
        shfile.write("    rim_variant=%s" % (variant[1:]))
        shfile.write("}")
    xmlfile.close()
    #
    # add the nodeList to the shell - to help out install scripts
    s="nodeNames=("
    for nodeName in nodeList:
        s+="%s " % (nodeName)
    s+=")"
    shfile.write(s);
    shfile.write("numNodes=%d" % (len(nodeList)))
    shfile.close()
    #
    # go through App+Product+Amfi+Services+Components and create a flat dict suitable
    # for consumption by pythons scripts though the rim module's getVars() method.
    varlist={}
    # app
    varlist.update(env.rim.app.varList())
    # product
    varlist.update(env.rim.prod.varList())
    # nodes of the product
    for amfi in env.prod.nodes:
        varlist.update(env.prod.nodes[amfi].varList())
    for serviceName in env.app.services:
        varlist.update(env.app.services[serviceName].varList())
        for compName in env.app.components:
            varlist.update(env.app.components[compName].varList())
    # Since all services and component variables are agregated to the amfi
    # we shoudl have everything we need. Maybe we need CML and other platform model
    # variables as well...[future]
    varfile.write("{\n")
    for key in sorted(varlist.keys()):
        varfile.write('    "%s" : "%s",\n' %( key, varlist[key].replace('"', '\\"') ))
    varfile.write("}\n")
    
    #
    # That is the signal we can increment the build number
    #
    env.rim.incBuildNumber(dirUp)
    return 0

#
# Build the final tar ball of everything needed to install on a target
#
def buildTarBall(target, source, env):
    print "Building final tarball : %s" % target[0].abspath
    mydir=os.path.dirname(target[0].abspath)
    srcdir=os.path.dirname(source[0].abspath)
    cmd="cd %s && rm -f %s/*.tgz && tar czf %s " % (srcdir, mydir, target[0].abspath)
    for s in source:
        cmd+="%s " % (os.path.basename(s.abspath))
    env.rim.command(cmd)
#
# Build a signed upgrade package out of the tarfile and a private key value
# source[0]=tar file
# source[1]=key file
#
def buildSignedUpg(target, source, env):
    print "Building signed upgrade package : %s" % target[0].abspath
    dir=os.path.dirname(target[0].abspath)
    tarname=os.path.basename(source[0].abspath)
    upgname=os.path.basename(target[0].abspath)
    cmd="cd %s && (cat %s | openssl sha1 -sign %s > signature)" % (dir, tarname, source[1].abspath)
    print "Creating signature...",
    env.rim.command(cmd)
    print "Done."
    print "Signing tarfile %s..." % tarname,
    cmd="cd %s && rm -f *.upg && (cat %s signature > %s.upg)" % (dir, tarname, tarname[:-4])
    env.rim.command(cmd)
    print "Done."
#
# Target that takes a binary and stamps it with current bld context vars
#
def buildTaggedProg(target, source, env):
    dst=target[0].abspath   
    src=source[0].abspath
    #
    # TODO = create a builder for an unfiltered rimTag.c.unf that would be colocated 
    # with this builder and so the tag and the space for the replcement can be all
    # handled here.
    # For now we need to make the defined tags and array sizes match between here
    # and $RIMROOT/build/rimTag.c
    #
    # NOTE: length of the below strings is exactly 100 characters to match arrasy sizes declared in rimtag.c
    dateKey="__TP_DATE_AND_TIME_KEY__                                                                           "
    tagKey ="__TP_BUILD_TAG_KEY__                                                                               "
    whoKey ="__TP_WHO_BUILT_IT_KEY__                                                                            "
    specKey="__TP_BUILD_SPEC_KEY__                                                                              "
    viewKey="__TP_BUILD_VIEW_KEY__                                                                              "
    padding="                                                                                                   "
    #
    # get the values for all these keys
    #
    who=os.environ["USER"]
    date=os.popen("date","r").readline().rstrip('\n')
    view=env.rim.branchname
    #
    # the value for the build number itself can come from
    # many places. In order -> OS environment, rim env, the application xml
    #
    tag=env.rim.getBldTag(env.compi.prod.repos)    
    #
    # Finaly, replace the keys with their values
    #
    cmd  ="cat %s | sed 's^%s^%s\\d0%s^'" % (src, dateKey, date, padding[0:len(padding)-len(date)-1])
    cmd +=" | sed 's^%s^%s\\d0%s^'"       % (tagKey, tag, padding[0:len(padding)-len(tag)-1])
    cmd +=" | sed 's^%s^%s\\d0%s^'"       % (whoKey, who, padding[0:len(padding)-len(who)-1])
    cmd +=" | sed 's^%s^%s\\d0%s^'"       % (viewKey, view, padding[0:len(padding)-len(view)-1])
    cmd += " > %s" % (dst)
    print "Tagging program %s" % dst
    env.rim.command(cmd)
    os.chmod(dst, 0755)

def registerBuilders(env):
    bldModule = Builder.Builder(action = buildModule,suffix = '.fs',src_suffix = '')	
    bldBom = Builder.Builder(action = buildBom,suffix = '.bom',src_suffix = '')	
    bldTaggedProg = Builder.Builder(action = buildTaggedProg, suffix="", src_suffix = '.unt')	
    bldTarBall = Builder.Builder(action = buildTarBall, suffix=".tgz", src_suffix = '')	
    bldSignedUpg = Builder.Builder(action = buildSignedUpg, suffix=".upg", src_suffix = '')	
    env['BUILDERS']['TaggedProg']=bldTaggedProg
    env['BUILDERS']['Module']=bldModule
    env['BUILDERS']['Bom']=bldBom
    env['BUILDERS']['TarBall']=bldTarBall
    env['BUILDERS']['SignedUpg']=bldSignedUpg
