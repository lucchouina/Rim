
from select import *
import rim
import os
import sys
import time

#
# class to handle select operations
#
class selector():
    
    def __init__(self, exitOnEmpty=True):
        self.handlers=[]
        self.done=False
        self.exit=exitOnEmpty
        self.log=rim.logger("selector").log
        
    def addHandler(self, handler):
        self.log("New handler %s" % handler)
        self.handlers.append(handler)
        
    def waitLoop(self, timeout=1):
    
        for h in self.handlers: h.initHandles()
        again=True
        
        while again:
            rlist=[]
            wlist=[]
            xlist=[]
            
            for h in self.handlers: h.setHandles(rlist, wlist, xlist)

            try:
                rlist, wlist, xlist = select(rlist, wlist, xlist, timeout)
            except error as (code, strerr):
                self.log("error %d '%s'" % (code, strerr))
                time.sleep(1)
                continue
            except:
                return
                
            for h in self.handlers: 
                again=h.chkHandles(rlist, wlist, xlist)
                if not again : 
                    if self.exit: # backward compatibility
                        self.log("exiting")
                        break
                    else:
                        h.releaseHandles()
                        del(self.handlers[self.handlers.index(h)])
                
            if not len(self.handlers): break
        
        for h in self.handlers: h.releaseHandles()
            
 
