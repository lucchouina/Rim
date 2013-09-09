from SCons.Tool import gcc
import SCons.Util
import RimUtils
"""
	Include gcc and overide the bin paths to point to our cross build location
"""
#bins=[ "CC", "LINK", "AS", "AR", "CXX" ]
bins=[ "CC", "AS", "AR", "CXX" ]

def generate(env, toolsPath):
    gcc.generate(env)
    #for bin in bins:
    #    #env[bin] = "/net/172.16.192.192/home/tools/rim/xcomp/wrl_30/i586-wrs-linux-gnu/bin/i586-wrs-linux-gnu-"+env[bin]
    #    env[bin] = "/net/172.16.192.192/home/tools/rim/xcomp/build-install/bin/"+env[bin]
