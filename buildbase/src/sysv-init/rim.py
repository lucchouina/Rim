Import('env')
import Rim
rim=Rim.Rim(env)

src="""
    init.c
    utmp.c
""".split()

rim.addCflags("-ansi -O2 -fomit-frame-pointer -W -Wall -D_GNU_SOURCE -DINIT_MAIN");

rim.Program("init", src);
