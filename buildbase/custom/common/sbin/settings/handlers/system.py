#!/usr/bin/env python

""" discovery.py

discovery functions

"""

import json
import os
from settings.command import *

myId="System"
INITMODE_FILE = "/etc/initmode"
ENABLE_DISCOVERY_ATTR="EnableDiscovery"
ENABLE_INITMODE_ATTR="EnableInitmode"
GOTO_ATTR="goto"
UPTIME_ATTR="uptime"

def uptime():
 
     try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
     except:
        return "???"
 
     total_seconds = float(contents[0])
 
     # Helper vars:
     MINUTE  = 60
     HOUR    = MINUTE * 60
     DAY     = HOUR * 24
 
     # Get the days, hours, etc:
     days    = int( total_seconds / DAY )
     hours   = int( ( total_seconds % DAY ) / HOUR )
     minutes = int( ( total_seconds % HOUR ) / MINUTE )
     seconds = int( total_seconds % MINUTE )
 
     # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
     string = ""
     if days > 0:
         string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
     if len(string) > 0 or hours > 0:
         string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
     if len(string) > 0 or minutes > 0:
         string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
     string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )
 
     return string;

def get():
    """ retrieve the current discovery setting """
    result = {}
    result[ENABLE_INITMODE_ATTR] = os.path.exists(INITMODE_FILE)
    result[UPTIME_ATTR] = uptime()
    result[GOTO_ATTR] = "Current"
    return result
    
def isInitmode(cfg):
    return cfg[ENABLE_INITMODE_ATTR]

def set(old, new):
    """ update discovery settings in avahi """
    
    # be friendly to development environment
    cmd=""
    new_values=new[myId]
    goto=new_values[GOTO_ATTR]
    if os.path.isdir("/pivot") or os.path.isdir("/curroot/pivot"):
        if new_values[ENABLE_INITMODE_ATTR]:
            run_command("sed -i -e 's/id:5:initdefault:/id:3:initdefault:/g' /etc/inittab")
            run_command("touch %s" % INITMODE_FILE)
            cmd = "%s\nsleep 5;\ntelinit 3" % cmd
        else:
            run_command("sed -i -e 's/id:3:initdefault:/id:5:initdefault:/g' /etc/inittab")
            run_command("rm -f %s" % INITMODE_FILE)
            cmd = "%s\ntelinit 5" % cmd

        # in the case a new goto state was selected , we do not have to tell init anything
        # the initmode flag has been persisted above ...
        # so override the cmd,
        if goto.lower() != "current":
            if goto.lower() == "reboot":
                cmd="reboot"
            elif goto.lower() == "shutdown":
                cmd="halt"
            elif goto.lower() == "revert":
                cmd="rimRevert"
            elif goto.lower() == "reset" or goto.lower() == "reset to factory":
                cmd="rimReset"
    else: # only reboot and halt on dev systems
        if goto.lower() !="current":
            if goto.lower() =="reboot":
                cmd="reboot"
            elif goto.lower() == "shutdown":
                cmd="halt"
    return cmd
    
# translate config during upgrade
# We moved the initmode under the system block now
def translate(incoming, outgoing):
    if incoming.has_key('Initmode'):
        outgoing[myId]={}
        outgoing[myId][ENABLE_INITMODE_ATTR]=incoming['Initmode'][ENABLE_INITMODE_ATTR]
        outgoing[myId][GOTO_ATTR]='current'
    else:
        outgoing[myId]=incoming[myId]

def schema():
    return """
        "%s": {
            "type":"map",
            "title":"System",
            "order":"4",
            "description":"System life cycle and state configuration",
            "note":
                "Important: If you used the Bonjour-discovered IP address to access this configuration page, be sure that you can access this page using the static IP  address configured above before clearing the check box below to disable initmode. Disabling initmode makes this page unavailable and disables Bonjour.",
            "mapping":
            {
                "%s": {
                    "type":"bool",
                    "initmode":true,
                    "appmode":true,
                    "required":true,
                    "title": "Enable initmode",
                    "description":"Enable initmode"
                },
                "%s": {
                    "type":"str",
                    "access":"write-only",
                    "initmode":true,
                    "appmode":true,
                    "title": "Go to state: ",
                    "description":"List of possible system states",
                    "enum": [ "Current", "Revert", "Reset", "Reboot", "Shutdown" ]
                 },
                "%s": {
                    "initmode":true,
                    "appmode":true,
                    "type":"str",
                    "access":"read-only",
                    "title": "System uptime",
                    "description":"System uptime"
                }
            }
        }
        
""" % (
    myId, 
    ENABLE_INITMODE_ATTR,
    GOTO_ATTR,
    UPTIME_ATTR
)

def cfgKey():
    return myId
    
if __name__ == '__main__':
    print json.dumps(get_timezones())


