from SCons.Tool import gcc
import SCons.Util
import RimUtils
"""
	Include gcc and overide the bin paths to point to our cross build location
"""

bins={
	"CC" : "gcc", 
	"AS" : "gas", 
	"AR" : "ar", 
	"CXX": "g++" 
}

def generate(env, toolsPath):
    gcc.generate(env)
    for bin in bins:
        #env[bin] = "/svn/v_4_1_4/Linux_2.6/arm-2007q3/bin/arm-none-linux-gnueabi-"+env[bin]
        #
        #env[bin] = "/home/lchouinard/work/armxcomp/toolchain_arm/bin/arm-linux-gnueabi-"+env[bin]
        env[bin] = "%s/bin/arm-linux-gnueabi-%s" % (toolsPath,bins[bin])
    env['LINK']='$SMARTLINK'
    env['SHLINKCOM']=env['SHLINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
    env['LINKCOM']=env['LINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
