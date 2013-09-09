#!/usr/bin/env python
#

""" dns.py

JSON for reading/updating name resolution Settings

"""
import os
import json

from settings.command import *
from settings.utils import *

myId="DNS"
DNS1_ATTR="DNS1"
DNS2_ATTR="DNS2"
NAME_ATTR="Name"
DOMAIN_ATTR="Domain"
HOSTNAME_FILE = "/etc/hostname"
DOMAINNAME_FILE = "/etc/domainname"

ALL_ATTRS=[ NAME_ATTR, DOMAIN_ATTR, DNS1_ATTR, DNS2_ATTR ]

def get():
    """ retrieve IP settings """
    dnsServers = run_command_lines("grep 'nameserver' /etc/resolv.conf | sed -e 's/nameserver[[:space:]]*//'")
    
    result = {}
    
    result[NAME_ATTR] = run_command_one_line("cat %s 2>/dev/null" % HOSTNAME_FILE)
    if not len(result[NAME_ATTR]):
        result[NAME_ATTR] = run_command_one_line("hostname")
        
    result[DOMAIN_ATTR] = run_command_one_line("cat %s 2>/dev/null" % DOMAINNAME_FILE)
    if not len(result[DOMAIN_ATTR]):
        result[DOMAIN_ATTR] = run_command_one_line("domainname")
        if result[DOMAIN_ATTR] == "(none)":
            result[DOMAIN_ATTR]=""
            
    if len(dnsServers) > 0:
        result[DNS1_ATTR] = dnsServers[0]
    else:
        result[DNS1_ATTR] = ""
    
    if len(dnsServers) > 1:
        result[DNS2_ATTR] = dnsServers[1]
    else:
        result[DNS2_ATTR] = ""
                
    return result


def set(old, new):
    """ update IP settings conditionally
    """
    
    new_values=new[myId]
    hostname = new_values[NAME_ATTR]
    domain = new_values[DOMAIN_ATTR]
    
    #
    # this does it in the kernel...
    #
    cmd="hostname %s;" % hostname
    if len(domain):
        cmd= "%s%s" % (cmd, "domainname %s;" % domain)
        run_command("echo %s > %s" % (domain, DOMAINNAME_FILE))
    
    #
    # this does it on disk, although I believe this is supposed
    # to be only the 1st part of the name
    #
    f = open("/etc/hostname", "w")
    f.write(hostname)
    f.close()
    
    oldHostname=old[myId]['Name']
    
    #
    # Now fix up /etc/hosts, and /etc/mailname
    #
    replace_in_file("/etc/hosts", oldHostname, hostname, word=True)
    
    #
    # here's a pile of others...
    #
    replace_in_file("/etc/mailname", oldHostname, hostname)
    
    replace_in_file("/etc/ssh/ssh_host_dsa_key.pub", oldHostname, hostname)
    replace_in_file("/etc/ssh/ssh_host_rsa_key.pub", oldHostname, hostname)
    replace_in_file("/etc/ssmtp/ssmtp.conf", oldHostname, hostname)
    
    dns1 = new_values[DNS1_ATTR]
    dns2 = new_values[DNS2_ATTR]
    
    return _update_dns_settings(dns1, dns2, new[myId]['Domain'], cmd)
    
def setName(cfg, name):
    cfg[NAME_ATTR]=name
                   
def _update_dns_settings(dns1, dns2, domain, cmd):
    """ update dns settings with a couple of new values """

    f = open('/etc/resolv.conf.new', 'w')
    f.write("domain %s\n" % domain)
    f.write("search %s\n" % domain)
    
    if len(dns1):
        f.write("nameserver %s\n" % dns1)
    
    if dns1 != dns2 and len(dns2):
        f.write("nameserver %s\n" % dns2)
        
    #
    # For 'test' purposes, we need to make this way less then the default 10 seocnds...
    # (5 timeout x 1 retry). Below is 2 seconds
    f.write("options timeout:1 retry:1\n")
    
    f.close()
    return "%s mv /etc/resolv.conf.new /etc/resolv.conf" % cmd
        
# test the group. These values have been validated and activated
# and use wants to test their runtime 
#
# We have to do a gethostbyname() with minimal timeout.
# Since the socket timeout does not change the hostname resolution
# timout, we can wait up to 10 seconds to fail
# To work around that, we setup a signal handler and use SIGALRM.
#
def test(values, name, errors):
    import signal
    import socket 
    global lerrors
    def handler(signum, frame):
        lerrors.append("Timed out resolving www.google.com")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(2)
    socket.setdefaulttimeout(2)
    lerrors=[]
    try:
        socket.gethostbyname("www.google.com")
    except:
        pass
    signal.alarm(0)

    if len(lerrors): 
        errors[name]=lerrors[0]
        return False
    return True
    
def schema():
    return """
        "%s": {
            "type":"map",
            "order":"2",
            "title":"Name Resolution",
            "description":"List up to 2 DNS servers for proper name resolution.",
            "mapping":
            {
                "Name":
                {
                    "order":1,
                    "type":"str",
                    "required":true,
                    "initmode":true,
                    "title":"Host Name"
                },
                "Domain":
                {
                    "order":2,
                    "type":"str",
                    "subtype":"dns",
                    "required":true,
                    "initmode":true,
                    "title":"Domain"
                },
                "DNS1": 
                {
                    "order":3,
                    "type":"str",
                    "subtype":"ip",
                    "required":true,
                    "initmode":true,
                    "title":"DNS server 1"
                },
                "DNS2": 
                {
                    "order":4,
                    "type":"str",
                    "subtype":"ip",
                    "initmode":true,
                    "title":"DNS server 2"
                }
            }
        }
""" % myId

def cfgKey():
    return myId

    
if __name__ == '__main__':
    print json.dumps(get_ipinfo())
    
    
        
    

    



