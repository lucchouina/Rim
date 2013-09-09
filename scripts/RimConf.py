import sys
import os 
import glob
import string
import xml.dom.minidom
import inspect
import RimCore

#
# Read in all config specs for associate source control
#
class Branch:
    def __init__(self, node, filename):
        self.name=node.getAttribute('name')
        self.product=node.getAttribute('product')
        self.desc=node.getAttribute('desc')
        self.filename=os.path.basename(filename)
        self.scs={}
        self.parents={}
        self.revision={}
        for scsnode in node.getElementsByTagName('scs'):
            name=scsnode.getAttribute('name')
            self.scs[name]=scsnode.getAttribute('version')  
            self.parents[name]=scsnode.getAttribute('parent')
            revision=scsnode.getAttribute('revision')
            if len(revision) > 0:
                self.revision[name]=revision
            else:
                self.revision[name]='HEAD'
            

class Scs(RimCore.Variables):
    def __init__(self, node):
        self.name=node.getAttribute('name')
        self.repo=node.getAttribute('repo')
        self.prefix=node.getAttribute('prefix')
        self.archspecific=node.getAttribute('archSpecific')
        if not self.archspecific: self.archspecific="False"
        self.archspecific=eval(self.archspecific)

class Repo(RimCore.Variables):
    def __init__(self, node):
        self.name=node.getAttribute('name')
        self.server=node.getAttribute('server')
        self.port=node.getAttribute('port')
        self.type=node.getAttribute('type')
        self.contype=node.getAttribute('contype')
        self.root=node.getAttribute('root')

class Action():
    def __init__(self, node):
        self.name=node.getAttribute('action')
        self.script=node.firstChild.wholeText
        self.interpreter=node.getAttribute('interpreter')

class ScsType(RimCore.Variables):
    def __init__(self, node):
        self.name=node.getAttribute('name')
        self.subtrees=eval(node.getAttribute('subtrees'))
        self.actions={}
        for hook in node.getElementsByTagName('script'):
            action=Action(hook)
            self.actions[action.name]=action

import copy
def copyAttr(to, frm):
    for attr in vars(frm):
        if hasattr(frm, attr):
            setattr(to, attr, getattr(frm,attr))
        else:
            setattr(to, attr, '')
    
class Geo:
    def __init__(self, node, ref=None):
        attrs=node.attributes
        baseattrs=[ 
            'name', 
            'disks', 
            'probe', 
            'parts', 
            'rwcache', 
            'pprefix', 
            'stick', 
            'cdrom', 
            'raided',
        ]
        if ref: 
            copyAttr(self, ref)
        # make sure we have defaults for all base attributes
        for attr in baseattrs:
            if not hasattr(self, attr):
                setattr(self, attr, '')
        for key in attrs.keys():
            value=node.getAttribute(key)
            if value:
                setattr(self, key, value)
            elif not ref:
                setattr(self, key, '')
                
class Clm:
    def __init__(self, geos, node):
        self.name=node.getAttribute('name')
        RimCore.rimcore.dbg(2,"clmNode - %s", self.name)
        self.arch=node.getAttribute('arch')
        self.karch=node.getAttribute('karch')
        geonodes = node.getElementsByTagName('geo')
        preloaders=node.getElementsByTagName('preloader')
        if len(preloaders):
            self.preloader=preloaders[0].getAttribute('type')
        loaders=node.getElementsByTagName('loader')
        if len(loaders):
            self.loader=loaders[0].getAttribute('type')
        self.geonodes=[]
        for geonode in geonodes:
            refName=geonode.getAttribute('refname')
            if not refName:
                self.geonodes.append(Geo(geonode))
            else :
                if refName in geos:
                    self.geonodes.append(Geo(geonode, ref=geos[refName]))
                else:
                    print "Reference to geo '%s' not found in rim.xml clmNode" % refName
                    sys.exit(1)

class Loader:
    def __init__(self, node):
        self.type=node.getAttribute('type');
        

class Arch(Loader):
    def __init__(self, node):
        self.name=node.getAttribute('name');
        Loader(node.getElementsByTagName('loader')[0])
        
class Os:
    def __init__(self, node):
        self.fsbuilders={}
        self.name=node.getAttribute('name');
        self.fstype=node.getAttribute('fstype');
        fsnodes = node.getElementsByTagName('fsbuild')
        for fsnode in fsnodes:
            self.fsbuilders[fsnode.getAttribute('name')]=fsnode.firstChild.wholeText

class osArch:
    def __init__(self, node):
        self.name=node.getAttribute('name');
        self.tools=node.getAttribute('tools');
        self.target=node.getAttribute('target');

class Distro(osArch):
    def __init__(self, node):
        self.name=node.getAttribute('name');
        self.osBase=node.getAttribute('os');
        self.versions={}
        for verNode in node.getElementsByTagName('version'):
            vname=verNode.getAttribute('name')
            arches={}
            for archNode in node.getElementsByTagName('osArch'):
                oan=osArch(archNode)
                arches[oan.name]=oan
            self.versions[vname]=arches

def getChildrenByTagName(node, tagName):
    matches=[]
    for child in node.childNodes:
        if child.nodeType==child.ELEMENT_NODE and (child.tagName==tagName):
            matches.append(child)
    return matches
        
class Tool(RimCore.Variables):
    def __init__(self, node, tset):
        self.initVars(tset)
        self.addVars(tset, self)
        self.getVars(node);
        self.name=node.getAttribute('name');
        self.options=self.translate(node.getAttribute('options'));
        self.version=node.getAttribute('version');
        self.tset=tset # cross ref

class toolSet(RimCore.Variables):
    def __init__(self, node, obj):
        self.initVars(obj)
        self.addVars(obj, self)
        self.getVars(node);
        self.name=node.getAttribute('name');
        self.release=node.getAttribute('osRelease');
        self.arch=node.getAttribute('arch');
        self.version=node.getAttribute('version');
        self.target=node.getAttribute('target');
        self.tools={}
        for toolNode in getChildrenByTagName(node, 'tool'):
            t=Tool(toolNode, self)
            self.tools[t.name]=t

class RimConf(RimCore.Variables):
    def __init__(self):
        #
        # Test for proper environment setup
        #
        if not os.environ.has_key('RIM_WORKSPACE'):
            print "What about RIM_WORKSPACE dude!?"
            sys.exit(1)
        workspace=os.environ['RIM_WORKSPACE']
        self.addVar("RIM_WORKSPACE", "ENV")

        #
        # load the base Rim config
        mypath="/".join(os.path.abspath(__file__).split("/")[0:-1])        
        rimConf = xml.dom.minidom.parse("%s/rim.xml" % mypath)
        if not rimConf:
            print "Invalid RIM config file "+document
            print "Please fix any errors listed in the above output before continuing."
            sys.exit(1)

        self.clms={}
        self.geos={}
        self.arches={}
        self.oses={}
        self.distros={}
        self.toolsets={}

        self.workspace=os.getenv("RIM_WORKSPACE")
        self.branchname=os.getenv("RIM_BRANCH")
        self.rimtagRoot="${RIMROOT}/src/rimtag"
        #
        # only thing we pick up is the BLDROOT and RIMROOT
        #
        rn=rimConf.getElementsByTagName('rim')[0]
        self.addVar("ver", rn.getAttribute('version'))
        self.addVar("HOME", "ENV")
        self.getVars(rn)
        
        #
        # create the geoNodes entries
        self.geoNodes=rimConf.getElementsByTagName('geoRef')
        for geoNode in self.geoNodes:
            geo=Geo(geoNode);
            # create a dict of all cml nodes
            self.geos[geo.name] = geo;                            
        #
        # create the cmlNodes entries
        self.clmNodes=rimConf.getElementsByTagName('clmNode')
        for clmNode in self.clmNodes:
            cn=Clm(self.geos, clmNode);
            # create a dict of all cml nodes
            self.clms[cn.name] = cn;                            
        #
        # Add the top most custom directory here
        self.commonRoot=self.getVar("customRoot")
        #
        # Arch'es
        #
        # create the archNodes entries
        self.archNodes=rimConf.getElementsByTagName('arch')
        for archNode in self.archNodes:
            an=Arch(archNode);
            # create a dict of all arch nodes
            self.arches[an.name] = an;
        #
        # OS'es
        #
        # create the oses entries
        self.osNodes=rimConf.getElementsByTagName('os')
        for osNode in self.osNodes:
            on=Os(osNode);
            self.oses[on.name] = on;
        #
        # Distributions
        #
        # create the distroNodes entries
        self.distroNodes=rimConf.getElementsByTagName('distro')
        for distroNode in self.distroNodes:
            rn=Distro(distroNode);
            self.distros[rn.name] = rn;
        #
        # Tools
        #
        self.toolXmlNodes=rimConf.getElementsByTagName('toolSet')
        for toolNode in self.toolXmlNodes:
            ts=toolSet(toolNode, self);
            self.toolsets[ts.name] = ts;
        #
        # read in source control items.
        #
        Nodes=rimConf.getElementsByTagName('scstypes')[0]
        self.scstypes={}
        for scstypeNode in Nodes.getElementsByTagName('scstype'):
            scstype=ScsType(scstypeNode)
            self.scstypes[scstype.name]=scstype
        Nodes=rimConf.getElementsByTagName('repositories')[0]
        self.repos={}
        for repoNode in Nodes.getElementsByTagName('repo'):
            repo=Repo(repoNode)
            self.repos[repo.name]=repo
        Nodes=rimConf.getElementsByTagName('sources')[0]
        self.scs={}
        for scsNode in Nodes.getElementsByTagName('scs'):
            scs=Scs(scsNode)
            self.scs[scs.name]=scs
        #
        # defined branches of products
        self.branches={}
        branchDir="%s/branches" % workspace
        for branchFile in glob.glob('%s/*' % branchDir):
            thisName=branchFile.split("/")[-1]
            if thisName != "bootbranch" :
                try:
                    branchXml=xml.dom.minidom.parse(branchFile)
                except Exception as e:
                    print "Error processing branch file '%s'!" % branchFile
                    print e
                    sys.exit(1)
                for branchNode in  branchXml.getElementsByTagName('branch'):
                    branch=Branch(branchNode, branchFile)
                    if branch.name in self.branches:
                        print "duplicate spec name '%s' found in file(s) - %s and %s" % (
                            branch.name, branch.filename, self.branches[branch.name].filename
                        )
                        sys.exit(1)
                    self.branches[branch.name]=branch
        if self.branchname not in self.branches:
            sys.stderr.write("Branch '%s' not found. \nUse 'rimbranch -l' to list available branches'\n" % self.branchname)
            sys.exit(1)
        self.branch=self.branches[self.branchname]
        rootversion=self.branch.scs['roots']
        self.rootsroot="%s/roots_%s" % (self.workspace, rootversion)
