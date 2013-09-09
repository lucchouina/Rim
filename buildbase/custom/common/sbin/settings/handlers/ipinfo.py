#!/usr/bin/env python
#

""" ipinfo.py

JSON for reading/updating IP Settings

"""
import os
import json
import subprocess

from settings.command import *
from settings.utils import *

myId="IPInfo"
IP_ADDRESS_ATTR="IPAddress"
# Warning - below is used in container.py class 
SUBNET_MASK_ATTR="SubnetMask"
GATEWAY_ATTR="Gateway"
BCAST_ATTR="Bcast"
IFACE_ATTR="iface"

CFG_FILE="/etc/network/interfaces"

ALL_ATTRS=[ IP_ADDRESS_ATTR, SUBNET_MASK_ATTR, GATEWAY_ATTR ]

# we depend on something else changing, namely the hosts IpAddress
def interests():
    return { setInitMode : { "System" : "'EnableInitmode" } }

# ip address has changed
def setInitMode(old, new):
    writeInterfaceFile(new)
    return "service network restart\n"  

#
# return the active configuration.
# this will only happen on a development system using dhcp 
#
def ifconfig():
    result={}
    cmd="ifconfig eth0"
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    line=child.stdout.readline()
    line=child.stdout.readline()
    address=line.split()[1].split(":")[1]
    netmask=line.split()[3].split(":")[1]
    cmd="ip -f inet route | grep default"
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    line=child.stdout.readline()
    if len(line) > 0:
        gateway=line.split()[2]
    
    result[IP_ADDRESS_ATTR] = address
    result[SUBNET_MASK_ATTR] = netmask
    result[GATEWAY_ATTR] = gateway
    return result

isDhcp=False

def getBcast(cfg):
    bcast=[]
    faddr=cfg[IP_ADDRESS_ATTR].split('.')
    fmask=cfg[SUBNET_MASK_ATTR].split('.')
    for idx in range(0, len(faddr)):
        v=int(faddr[idx]) & int(fmask[idx]) 
        bcast.append("%d" % v)
    return ".".join(bcast)
    
    

def get():
    """ retrieve IP settings """
    result={}
    isDhcp=False
    #
    # We assume that only one interface is visible and configurable by the user
    #
    f=open(CFG_FILE, "r")
    iface=""
    address=""
    netmask=""
    gateway=""
    line=f.readline()
    while len(line):
        fields=line.split()
        if len(fields) and fields[0][0] != '#':
            if fields[0]=="iface":
                if fields[3] == "static":
                    iface=fields[1]
                elif len(iface):
                    break;
            elif fields[0]=="address": address=fields[1]
            elif fields[0]=="netmask": netmask=fields[1]
            elif fields[0]=="gateway": gateway=fields[1]
        line=f.readline()
    
    result[IP_ADDRESS_ATTR] = address
    result[SUBNET_MASK_ATTR] = netmask
    result[GATEWAY_ATTR] = gateway
    
    if len(address) == 0:
        ifDhcp=True
        return ifconfig()
   
    return result
    
def getNetmask(cfg):
    return cfg[SUBNET_MASK_ATTR]

def getIp(cfg):
    return cfg[IP_ADDRESS_ATTR]

def setIp(cfg, ip):
    cfg[IP_ADDRESS_ATTR]=ip

def getGw(cfg):
    return cfg[GATEWAY_ATTR]

def writeInterfaceFile(new):
    
    baseDev="eth0" # need to make this track bonjourInterfaces from config
    
    new_values=new[myId]
    initmode=new['System']['EnableInitmode']
            
    ipAddress = new_values[IP_ADDRESS_ATTR]
    subnetMask = new_values[SUBNET_MASK_ATTR]
    gateway = new_values[GATEWAY_ATTR]

    f = open(CFG_FILE, 'w')
    
    f.write("auto lo\n")
    f.write("iface lo inet loopback\n")
    f.write("\n")
    
    if initmode : staticDev = "%s:static" % baseDev
    else: staticDev = baseDev
    
    f.write("auto %s\n" % staticDev)
    f.write("iface %s inet static\n" % staticDev)
    f.write("address %s\n" % ipAddress)
    f.write("netmask %s\n" % subnetMask)
    f.write("gateway %s\n" % gateway)
    f.write("\n")
    
    if initmode:
        f.write("auto %s\n" % baseDev)
        f.write("iface %s inet dhcp\n" % baseDev)
        
    f.close()
  
def set(old, new):
    """ update ip settings
    
    This is in /etc/network/interfaces. The ip address is also,
    however, stored in /etc/hosts (whichever entry matches `hostname`)
    """
    
    # turn to read-only on dhcp / development systems
    get()
    if isDhcp: return
    
    new_values=new[myId]
    ipAddress = new_values[IP_ADDRESS_ATTR]
    subnetMask = new_values[SUBNET_MASK_ATTR]
            
    # because of sequencing between hostname and ipinfo handlers we need to
    # try with both new and old hostname for the 'grep and replace' below
    hostname=new['DNS']['Name']
    oldname=old['DNS']['Name']
    replace_line_in_file("/etc/hosts", hostname, "%s     %s" % (ipAddress, hostname))
    replace_line_in_file("/etc/hosts", oldname, "%s     %s" % (ipAddress, hostname))
    
    writeInterfaceFile(new)
    return "restart network; importnet.sh 2>/dev/null 1>&2"

def schema():
    return """
        "%s": {
            "type":"map",
            "order":"1",
            "title":"IP Configuration",
            "description":"Ip network configuration",
            "mapping":
            {
                "%s": 
                {
                    "type":"str",
                    "order": 3,
                    "subtype":"ip",
                    "required":true,
                    "initmode":true,
                    "title":"Gateway"
                }, 
                "%s":
                {
                    "type":"str",
                    "order": 1,
                    "subtype":"ip",
                    "required":true,
                    "initmode":true,
                    "title":"IP Address"
                }, 
                "%s":
                {
                    "type":"str",
                    "order": 2,
                    "subtype":"netmask",
                    "required":true,
                    "initmode":true,
                    "title":"Network Mask"
                }
            }
        }
""" % (myId, GATEWAY_ATTR, IP_ADDRESS_ATTR, SUBNET_MASK_ATTR)

def ipv4_cidr_to_netmask(bits):
    """ Convert CIDR bits to netmask """
    netmask = ''
    for i in range(4):
        if i:
            netmask += '.'
        if bits >= 8:
            netmask += '%d' % (2**8-1)
            bits -= 8
        else:
            netmask += '%d' % (256-2**(8-bits))
            bits = 0
    return netmask
    
def ipToInt(ip):
    val=0
    for x in ip.split('.'):
        val = (256*val)+int(x)
    return val

# ref : http://en.wikipedia.org/wiki/IPv4
def reservedNetwork(network, nBits):
    
    reservedClassAs=[ 0, 127 ]
    reservedClassBs=[ ipToInt('169.254')  ]
    reservedClassCs=[ ipToInt('192.88.99'), ipToInt('192.0.2') , ipToInt('192.0.0')]
    reservedClassMult=[ ipToInt('224')>>4,  ipToInt('240')>>4 ]
    
    classMult=(network & 0xf0000000) >> 28
    classA=(network & 0xff000000) >> 24
    classB=(network & 0xffff0000) >> 16
    classC=(network & 0xffffff00) >>  8
    if classA in reservedClassAs and nBits >= 8:
        return True;
    if classB in reservedClassBs and nBits >= 16:
        return True;
    if classC in reservedClassCs and nBits >= 24:
        return True;
    if classMult in reservedClassMult and nBits >= 4:
        return True;
    return False

def validate(values, name, errors):
    error=""
    allValidNetworks=map(lambda x: ipv4_cidr_to_netmask(x), range(0,33))
    #
    # check that the network mask is valid
    if not values[SUBNET_MASK_ATTR] in allValidNetworks:
        error="Not a valid network mask value"
    else:
        # we have a valid mask i.e. a series of 1's followed by a series of 0's
        nBits=allValidNetworks.index(values[SUBNET_MASK_ATTR])
        #
        # make sure the gateway is routable through interface
        m_ip=ipToInt(values[IP_ADDRESS_ATTR])
        m_gw=ipToInt(values[GATEWAY_ATTR])
        m_mask=ipToInt(values[SUBNET_MASK_ATTR])
        #
        # do some standard validation on the network itself.
        # ref : http://en.wikipedia.org/wiki/IPv4
        #
        nBits=allValidNetworks.index(values[SUBNET_MASK_ATTR])
        network=m_ip & m_mask
        broadcast=network | (m_mask^0xffffffff)
        # network check
        if reservedNetwork(network, nBits):
            error="Invalid reserved network specified"
        else:
            # broadbast test
            if m_ip == broadcast:
                error="Invalid use of broacast address"
            else:
                if ( m_ip & m_mask ) != ( m_gw & m_mask ):
                    error="Cannot reach gateway using this ip address and mask"
    if error:
        errors[name]=error
        return False
    return True
#
# test the group. These values have been validated and activated
# and caller wants to test their runtime 
#
# For ip, it is really only testing if the gateway is available
#
def test(values, name, errors):
    # try to ping the gateway
    cmd="ping -c 1 -w 2 %s 2>/dev/null 1>&2" % values[GATEWAY_ATTR]
    if subprocess.call(cmd, shell=True):
        errors[name]="Cannot ping gateway"
        return False
    return True
    
def cfgKey():
    return myId
    
if __name__ == '__main__':
    print json.dumps(get_ipinfo())
