#!/usr/bin/env python
#
# Extract all librarie dependencies.
#
# Each module must define a level which is layer number it belongs too.
# There are 4 layers.
# 1) initrd, 2) os level, 3) application wide and 4) amf node specific
#
import os
import traceback
import RimElf
import RimCore
import re
class ELFException(Exception): pass

global libs
libs={}

blackList="""
    libgcc_s.so.1
""".split()

class libEntry:
    def __init__(self, level, libpath, relpath, mod):
        if mod:
            RimCore.rimcore.dbgLib(libpath, "mod is %s", mod.name);
        self.level=level;
        self.libpath=libpath
        self.relpath=relpath
        self.mod=mod
        self.kids=[]

class rimLibHandle:

    def __init__(self, amfi, mod):
        if amfi:
            self.key=amfi.osKey()
        else:
            self.key="test"
        self.amfi=amfi;
        self.mod=mod;
        if not libs.has_key(self.key):
            libs[self.key]={}
        self.re=re.compile("lib.*\.so.*")
        self.re2=re.compile("ld-linux*\.so.*")
        os.system("mkdir -p %s/logs" % amfi.product.repos);
        self.libFile=open("%s/logs/libs.log" % amfi.product.repos , "w")

    def searchSection(self, efile, s):
        # read that section in
        efile.seek(s.sh_offset)
        strs=efile.read(s.sh_size)
        names=strs.split('\x00')
        # scan it for matches
        matches=[]
        for s in names:
            matches+=self.re.findall(s)
            matches+=self.re2.findall(s)
        RimCore.rimcore.dbg(2, "matches = %s", matches)
        return matches
    
    def extractLibs(self, elfName, level, llist):
        elf=RimElf.ELFObject()
        ret=0
        try:
            efile=open(elfName, "r")
        except Exception, details:
            if RimCore.rimcore.dbglvl >= 3:
                print "Failed Elf scan of - "+elfName
                print "Stack back trace :"
                print "------------------------------"
                traceback.print_exc()
                print "------------------------------"
                print details
            self.libFile.write("========== Caught exception! ================"); 
        else:
            try:
                elf.fromFile(efile)
            except ELFException: 
                pass
            except:
                self.libFile.write("Elf fromfile exception on '%s'" % (elfName))
                pass
            else:
                for s in elf.getSections():
                    if s.sh_type == s.SHT_STRTAB:
                        # found a string section which could contain
                        # the library dependencies.
                        llist+=self.searchSection(efile, s)
                ret=elf.is64
            efile.close()
        return ret
    
    def levelDown(self, libList, keyLibEnt, level,dbglev):
        self.libFile.write("%*s LevelDown - level=%d key=%s from module %s to module %s\n" % (dbglev*4,"",level,keyLibEnt, libList[keyLibEnt].mod.name, self.mod.name))
        RimCore.rimcore.dbgLib(libList[keyLibEnt].libpath, "levelDown %s[%d] to %s[%d]", libList[keyLibEnt].mod.name, libList[keyLibEnt].level, self.mod.name, level)
        if level < libList[keyLibEnt].level:
            libList[keyLibEnt].level=level
            libList[keyLibEnt].mod=self.mod
        self.libFile.write("%*s kids are :" % (dbglev*4,""))
        for kid in libList[keyLibEnt].kids:
            self.libFile.write("%*s     kid=%s\n" % (dbglev*4,"",kid))
        for kid in libList[keyLibEnt].kids:
            self.levelDown(libs[self.key], kid, level, dbglev+1)
    
    def insertLib(self, lib, libpath, relpath, lookUpCb, level, prime, dbglev):
        # insert a library into the tree 
        # this call will recurse if this path is new to the list
        self.libFile.write("%*s InsertLib - key %s (%s,%s,%s,%d,%d) - have key = %d\n" % (dbglev*4,"",self.key,lib,libpath,relpath,level,prime,libs[self.key].has_key(libpath)))
        if not libs[self.key].has_key(libpath):
            # recurse down
            RimCore.rimcore.dbgLib(lib, "[%d] insertLib level=%d prime=%d", dbglev, level, prime)
            libs[self.key][libpath]=libEntry(level, libpath, relpath, self.mod)
            if not self.isBlack(lib):
                libs[self.key][libpath].kids=self.addLibs(libpath, lookUpCb, level, prime, dbglev+1)
        elif level < libs[self.key][libpath].level:
            # if we changed level and it's lower move all of them back
            RimCore.rimcore.dbgLib(lib, "[%d] Level ajust %d versus %d", dbglev, level, libs[self.key][libpath].level)
            self.levelDown(libs[self.key], libpath, level, dbglev)
           
    def isBlack(self,name):
        try:
            index=blackList.index(name)
            return True
        except:
            return False
            
        
    # add all libaries from an Elf object to this list
    def addLibs(self, elfName, lookUpCb, level, prime, dbglev=0):
        RimCore.rimcore.dbg(2, "%*sAdding lib %s", dbglev*4, "", elfName)
        newLibs=[]
        is64=self.extractLibs(elfName, level, newLibs)
        RimCore.rimcore.dbg(2, "%*s %s", dbglev*4, "", newLibs)
        paths=[]
        self.libFile.write("%*s AddLibs - Exe name [%s] - level=%d prime=%d - library list is :\n" % (dbglev*4,"",elfName, level, prime))
        for lib in newLibs:    
            (libpath, relpath)=lookUpCb(lib, is64)
            self.libFile.write("0%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
        for lib in newLibs:           
            (libpath, relpath)=lookUpCb(lib, is64)
            self.libFile.write("1%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
            if libpath and elfName != libpath:
                self.libFile.write("2%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
                paths.append(libpath)
                self.libFile.write("3%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
                self.insertLib(lib, libpath, relpath, lookUpCb, level, prime, dbglev)
                self.libFile.write("4%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
            self.libFile.write("5%*s     lib=[%s] libpath=[%s] relpath=[%s]\n" % (dbglev*4,"",lib, libpath, relpath))
        return paths
        
    def myLibs(self):
        liblist=[]
        for entry in libs[self.key]:
            if  libs[self.key][entry].mod == self.mod:
                self.libFile.write("myLibs %s owned by module %s\n" % (libs[self.key][entry].libpath, self.mod.name))
                RimCore.rimcore.dbgLib(libs[self.key][entry].libpath, "myLibs %s owned by module %s", libs[self.key][entry].libpath, self.mod.name)
                liblist.append([ libs[self.key][entry].libpath, libs[self.key][entry].relpath ])
        return liblist
                 
def test_cb(path):
    return ("/net/suntpus15/shares/rd/User/Chouinard.Luc/rim/roots/Linux/pnele/i386/3.0/usr/lib/"+path, "/net/suntpus15/shares/rd/User/Chouinard.Luc/rim/roots/Linux/pnele/i386/3.0/usr/lib/"+path);
             
if __name__ == '__main__':
    lhd=rimLibHandle(0, 0)
    lhd.inTest=1;
    lhd.addLibs("/net/suntpus15/shares/rd/User/Chouinard.Luc/rim/roots/Linux/pnele/i386/3.0/bin/bash", test_cb, 0, 0, 0, );
