import SCons.Util
"""
	Include gcc and overide the bin paths to point to our cross build location
"""
tpath="/opt/csw/gcc4/bin"
maps={
 "CC"           : "%s/gcc" % tpath,
 "LINK"         : "$SMARTLINK", 
 "AS"           : "/usr/ccs/bin/as", 
 "AR"           : "/usr/ccs/bin/ar", 
 "ARFLAGS"      : "cr",
 'ARCOM'        : '$AR $ARFLAGS $TARGET $SOURCES',
 "CXX"          : "%s/g++" % tpath,
}
#bins=[ "CC", "AS", "AR", "CXX", "SHCXX", "LINK", "SHCC"]
    
def generate(env, toolsPath):
    for bin in maps:
        env[bin] = maps[bin]
