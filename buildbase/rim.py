Import('env')
import Rim
rim=Rim.Rim(env)

dirs = """
  src
""".split()
rim.subdirs(dirs)
sourceTrees=dirs+[ "scripts", "custom", "python", "sbin", "etc" ]
