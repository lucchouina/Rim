Import('env')
import Rim
rim=Rim.Rim(env)

# this tree is used by multiple component
# 
if rim.getVar("COMPONENT") == "RimBase":
    dirs = """
        sysv-init
    """.split()
    if rim.getVar("ARCH") == "arm":
        dirs += [ "makedumpfile" ]

rim.subdirs(dirs)
