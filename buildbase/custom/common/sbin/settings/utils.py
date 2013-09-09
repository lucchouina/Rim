#!/usr/bin/env python

""" utils.py

various utilities shared by the other code

"""

from command import *
import simplejson as json

def initDefault():
    lines=open("/etc/inittab", "r").read().split('\n')
    for line in lines:
        fields=line.split(":")
        if len(fields) > 2 and fields[2] == 'initdefault':
            return int(fields[1])
    print "Could not figure out init default!?!?"
    sys.exit(1)
    

def validate_int(val, name, errors):
    """ validates that an attribute has an integer value """
    try:
        if int(val) != -1:
            return True
    except:
        pass
        
    errors[name]="Integer value required"
    return False

def validate_str(val, name, errors):
    return True

def validate_percent(val, name, errors):
    if not validate_int(val, name, errors):
        return False
    elif val < 0 or val > 100:
        errors[name]="Value must be between 0 and 100 incl."
        return False
    return True

def validate_ip(val, name, errors):
    error=""
    if len(val) == 0: return False
    components = val.split('.')
    if len(components) != 4:
        error="Format should be 'A.B.C.D'"
    else:
        for component in components:
            intVal = None
            try:
                intVal = int(component)
            except ValueError:
                error="X in X.X.X.X must be integer between 0 and 255 inclusive."
                break
            if intVal < 0 or intVal > 255:
                error="X in X.X.X.X must be between 0 and 255 incl."
                break
    if error:
        errors[name]=error
        return False
    return True

def ipv4_to_netmask(bits):
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
    
def validate_netmask(val, name, errors):
    #
    # check that the network mask is valid
    if not val in map(lambda x: ipv4_to_netmask(x), range(0,33)):
        errors[name]="Not a valid network mask value"
        return False
    return True


def validate_dns(val, name, errors):
    error=""
    if len(val) > 0:
        components = val.split('.')
        if len(components) == 1:
            error="invalid domain value" 
        else:
            for component in components:
                if len(component) == 0:
                    error="invalid domain value"
                    break
    if error:
        errors[name]=error
        return False
    return True

#
# routine to cleanup a config block prior to saving to storage
# all read-only or write-only variables need to tbe removed
#
def cleanCfg(schemaStr, id, cfg):
    schema=json.loads(schemaStr)
    clean={}
    mapping=schema[id]['mapping']
    for key in mapping:
        if cfg.has_key(key):
            if mapping[key].has_key('access'):
                access=mapping[key]['access']
                if access == "write-only" or access == "read-only":
                    continue;
            clean[key]=cfg[key]
    return clean
