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
        env[bin] = "%s/bin/i386-linux-gnu-%s" % (toolsPath,bins[bin])
    env['LINK']='$SMARTLINK'
    env.MergeFlags({'CCFLAGS' : ['-march=i486'] })
    env['SHLINKCOM']=env['SHLINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
    env['LINKCOM']=env['LINKCOM'].replace("$_LIBFLAGS","-Wl,--start-group $_LIBFLAGS -Wl,-end-group")
