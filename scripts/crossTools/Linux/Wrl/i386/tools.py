from SCons.Tool import gcc
import SCons.Util
import RimUtils
import string
"""
	Include gcc and overide the bin paths to point to our cross build location
"""
#bins=[ "CC", "LINK", "AS", "AR", "CXX" ]
bins=[ "CC", "AS", "AR", "CXX" ]

def replace(s, p1, p2):
    lst=s.split()
    lst2=[]
    for tok in lst:
        if tok==p1:
            lst2.append(p2)
        else:
            lst2.append(tok)
    return string.join(lst2)


def generate(env, toolsPath):
    gcc.generate(env)
    env['LINKCOM']=replace(env['LINKCOM'], '$_LIBFLAGS', '-Wl,--start-group $_LIBFLAGS -Wl,--end-group')
    env['SHLINKCOM']=replace(env['SHLINKCOM'], '$_LIBFLAGS', '-Wl,--start-group $_LIBFLAGS -Wl,--end-group')
    #
    # as we move from older to newer compilers lots of "warning: deprecated conversion from string constant to char*"
    # type of warnings. To remove these warnings we use the below compiler swaitch.
    xtraFlags="-Wno-write-strings"
    env.MergeFlags({'CCFLAGS' : xtraFlags.split() })
    for bin in bins:
        env[bin] = "%s/bin/%s-%s" % (toolsPath, env.amfi.tools.target, env[bin])
