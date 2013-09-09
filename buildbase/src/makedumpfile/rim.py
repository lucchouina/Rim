# standard rim linkage...
Import('env')
import Rim
rim=Rim.Rim(env)

VERSION="1.5.3"
DATE="19 Feb 2013"

commonSrc="""
    print_info.c 
    dwarf_info.c 
    elf_info.c 
    erase_info.c 
    sadump_info.c 
    cache.c
""".split()

rim.addCflags(("""
    -g 
    -O2 
    -Wall 
    -D_FILE_OFFSET_BITS=64
	-D_LARGEFILE_SOURCE 
    -D_LARGEFILE64_SOURCE
	-DVERSION='"%s"' 
    -DRELEASE_DATE='"%s"'
""" % (VERSION, DATE)).split())

rim.addLibs("""
    dw 
    bz2
    ebl
    dl
    elf
    z
""".split())

archMap={
    "i386" : "x86",
    "x86_64" : "x86_64",
    "arm" : "arm",
    "armv5" : "arm"
}
arch=rim.getVar("CPU")
if not arch in archMap:
    print "Failed to find arch '%s' as target CPU" % arch
    sys.exit(1)
arch=archMap[arch]
rim.addCflags([ "-D__%s__" % arch])
rim.Program("makedumpfile", [ "makedumpfile.c" ] + commonSrc+[ "arch/%s.c" % arch ])
