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
        env[bin] = "%s/bin/armv5-s2-linux-gnueabi-%s" % (toolsPath,bins[bin])
    env['LINK']=env['CXX']
    env['SHLINKCOM']=env['SHLINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
    env['LINKCOM']=env['LINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
