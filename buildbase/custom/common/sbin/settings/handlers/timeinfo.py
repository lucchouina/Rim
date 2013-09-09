#!/usr/bin/env python
#

""" timeinfo.py

JSON for reading/updating Time Settings

Attributes are:

NTPServer1/2/3: <dns name>
Timezone: <valid timezone

The list of valid timezones can be retrieved from Timezones.py, get_timezones()

The result (right now) looks something like:

{'NTPServer3': '', 'NTPServer2': 'pool.ntp.org', 'NTPServer1': 'ntp.ubuntu.com', 'Timezone': 'US/Eastern'}

"""

import json
import tempfile

from settings.command import *
from settings.utils import *

NTP_SERVER1_ATTR="NTPServer1"
NTP_SERVER2_ATTR="NTPServer2"
NTP_SERVER3_ATTR="NTPServer3"
ISOTIME_ATTR="IsoTime"
TIMEZONE_FILE="/etc/timezone"
TIMEZONES_DIR="/usr/share/zoneinfo"
TIMEZONE_ATTR="Zone"
NTP_CONF="/etc/ntp.conf"
myId="TimeInfo"

def ntpEnabled():
    return os.path.isfile(NTP_CONF)

# we depend on something else changing, namely the hosts IpAddress
def interests():
    return { doDnsChanges : { "DNS" :  ( "DNS1", "DNS2" ) } }
    
# ip address has changed
def doDnsChanges(old, new):
    return "service ntp restart"

def file_ok(name):
    """ filter to exclude particular patterns for a file name """
    if name[0] == '.' or \
       name.find("right") == 0 or \
       name.find("posix") == 0 or \
       name.find("Etc") == 0 or \
       name.find("SystemV") == 0:
        return False
    else:
        return True


def get_timezones():
    """ retrieve a list of timezones """    
    path = TIMEZONES_DIR
    
    timezones = []
    
    listing = os.listdir(path)
    
    for file1 in listing:
        if file_ok(file1):
            
            subpath = path + "/" + file1
            
            if os.path.isdir(subpath):
                
                sublisting = os.listdir(subpath)
                
                for file2 in sublisting:
                    
                    if file_ok(file2):
                        
                        timezones.append(file1 + "/" + file2)
                        
    timezones.sort()
    return timezones

def get():
    """ retrieve time settings """        

    t={}
    
    f = open(TIMEZONE_FILE, "r")
    tz = f.read()
    f.close()
    
    # get time in iso 8601 format
    from datetime import datetime, date, time
    t[ISOTIME_ATTR] = datetime.now().isoformat()
    
    t[TIMEZONE_ATTR] = tz.strip("\n")
    if ntpEnabled():
        ntpServers = run_command_lines("grep '^server' /etc/ntp.conf | grep -v '127.127.1.0' | sed -e 's/server[[:space:]]*//'")
        if len(ntpServers) > 0:
            t[NTP_SERVER1_ATTR] = ntpServers[0]
        else:
            t[NTP_SERVER1_ATTR] = ""

        if len(ntpServers) > 1:
            t[NTP_SERVER2_ATTR] = ntpServers[1]
        else:
            t[NTP_SERVER2_ATTR] = ""

        if len(ntpServers) > 2:
            t[NTP_SERVER3_ATTR] = ntpServers[2]
        else:
            t[NTP_SERVER3_ATTR] = ""
    
    return t
   
            
def set(old, new):
    """ set time settings conditionally """
                
    new_values=new[myId]

    tz = new_values[TIMEZONE_ATTR]
    l = get_timezones()
    if not tz in l:
        raise Exception("timezone not found in list")
        
    run_command("cp %s/%s /etc/localtime && echo %s > %s\n" % (TIMEZONES_DIR, tz, tz, TIMEZONE_FILE))
    if ntpEnabled():
        ntpServer1 = new_values[NTP_SERVER1_ATTR]
        ntpServer2 = new_values[NTP_SERVER2_ATTR]
        ntpServer3 = new_values[NTP_SERVER3_ATTR]

        tmpfileName = tempfile.mkstemp()[1]

        run_command("sed '/^server.*/,$d' /etc/ntp.conf > %s" % tmpfileName)

        f = open(tmpfileName, "a")

        f.write("server %s\n" % ntpServer1)

        if len(ntpServer2) > 0:
            f.write("server %s\n" % ntpServer2)

        if len(ntpServer3) > 0:
            f.write("server %s\n" % ntpServer3)

        f.close()

        run_command("sed '1,/^server.*/d' /etc/ntp.conf | sed '/^server.*/d' >> %s" % tmpfileName)
        run_command("cp /etc/ntp.conf /etc/ntp.conf.old && cp %s /etc/ntp.conf && rm %s\n" % (tmpfileName, tmpfileName))

        return "service ntp restart"
    return ""

#
# test the group. These values have been validated and activated
# and caller wants to test their runtime 
#
# For ip, it is really only testing if the gateway is available
#
def test(values, name, errors):
    # try to ping the gateway
    for s in [values[NTP_SERVER1_ATTR],values[NTP_SERVER2_ATTR],values[NTP_SERVER3_ATTR]]:
        if not len(s) : continue
        cmd="ntpdate -q -s -t 2 %s 1>/dev/null 2>&1" % s
        if not subprocess.call(cmd, shell=True): return True
        
    errors[name]="Cannot connect to ntp server(s)"
    return False

#
def schema():
    timezones=get_timezones()
    enumStr=""
    for zone in timezones:
        if len(enumStr) > 0: 
            enumStr='%s,\n "%s"' % (enumStr, zone)
        else:
            enumStr='"%s"' % (zone)
    ntpSchema="""
,
                "%s": 
                {
                    "type":"str",
                    "order":"1",
                    "access":"read-only",
                    "title":"Current time in ISO 8601 format"
                },
                "%s": 
                {
                    "type":"str",
                    "order":"1",
                    "subtype":"dns",
                    "initmode":true,
                    "required":true,
                    "title":"Time Server 1"
                },
                "%s": 
                {
                    "type":"str",
                    "order":"2",
                    "subtype":"dns",
                    "initmode":true,
                    "required":false,
                    "title":"Time Server 2"
                },
                "%s": 
                {
                    "type":"str",
                    "order":"3",
                    "subtype":"dns",
                    "initmode":true,
                    "required":false,
                    "title":"Time Server 3"
                }
""" % (
    ISOTIME_ATTR,
    NTP_SERVER1_ATTR,
    NTP_SERVER2_ATTR,
    NTP_SERVER3_ATTR,
)
    return """
        "%s": {
            "type":"map",
            "order":"10",
            "title":"Time Related Information",
            "description":"NTP servers and local timezone",
            "mapping":
            {
                "Zone":
                {
                    "type":"str",
                    "order":"4",
                    "initmode":true,
                    "required":true,
                    "title":"Timezone",
                    "description":"The timezone in which this host operates.",
                    "enum":
                    [
    %s
                    ]
                }%s
            }
        }
""" % (myId, enumStr, ntpSchema)

def cfgKey(): 
    return myId
    
if __name__ == '__main__':
    print json.dumps(get_timeinfo())

            
    

