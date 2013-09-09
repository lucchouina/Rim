#!/usr/bin/env python
#

""" build.py

Configuration handler for the read-only build info.

The build info is gathered via the repo 'Revision'  hook.
one of more component(s) of the product must have been flagged as a 
revision base.

"""
import subprocess
import json

myId="BuildInfo"
URL_ATTR='URL'
LCD_ATTR='Last Changed Date'
ROOT_ATTR='Repository Root'
LCA_ATTR='Last Changed Author'
LCR_ATTR='Last Changed Rev'
REV_ATTR='Revision'

def get_svninfo_from_file():
    """ retrieve build info from a file in the installed system"""
    try:
        f = open('/etc/buildinfo', 'r')
    except:
        # be friendly to global dev env for now
        try :
            f = open(PLASE_COMPONENT_ROOT_HERE, 'r')
        except:
            return {}
        
    d = f.read()
    f.close()
        
    return eval(d)
    
def get():
    """ retrieve svn info """
    t = None
    
    try:
        
        t = subprocess.Popen(('svn', 'info'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    except Exception:
        
        return get_svninfo_from_file()

    r = t.communicate()
    
    if len(r[0]) == 0:
        
        return get_svninfo_from_file()
        

    k = r[0].split('\n')
    
    l = {}
    
    for el in k:
        if len(el) > 0:
            attrval = el.split(': ')
            attr = attrval[0]
            val = attrval[1]
            
            if attr not in ('Path', 'Node Kind', 'Schedule', 'Repository UUID'):
                
                if attr == 'Last Changed Date':
                    val = val[0:val.index('(') - 1]
                
                #
                # remove spaces
                #
                attr = ''.join(attr.split(' '))
                
                if attr in ('LastChangedRev', 'Revision'):
                    val = int(val)
                    
                l[attr] = val
    return l
    
def set(old, new):
    # everything here is readonly
    return ""
    
def schema():
    return """
        "%s": {
            "type":"map",
            "hidden":"true",
            "order":"5",
            "title":"Build information",
            "description":"Version, date and other information about the current running build.",
            "mapping":
            {
                "%s": 
                {
                    "type":"str",
                    "order": 1,
                    "subtype":"str",
                    "readonly":true,
                    "title":"%s"
                }, 
                "%s": 
                {
                    "type":"str",
                    "order": 2,
                    "subtype":"str",
                    "readonly":true,
                    "title":"%s"
                }, 
                "%s": 
                {
                    "type":"str",
                    "order": 3,
                    "subtype":"str",
                    "readonly":true,
                    "title":"%s"
                }, 
                "%s": 
                {
                    "type":"str",
                    "order": 4,
                    "subtype":"str",
                    "readonly":true,
                    "title":"%s"
                }, 
                "%s": 
                {
                    "type":"int",
                    "order": 5,
                    "subtype":"int",
                    "readonly":true,
                    "title":"%s"
                }, 
                "%s": 
                {
                    "type":"int",
                    "order": 6,
                    "subtype":"int",
                    "readonly":true,
                    "title":"%s"
                }
            }
        }
""" % (
    myId,
    ''.join(URL_ATTR.split(' ')),
    URL_ATTR,
    ''.join(LCD_ATTR.split(' ')),
    LCD_ATTR,
    ''.join(ROOT_ATTR.split(' ')),
    ROOT_ATTR,
    ''.join(LCA_ATTR.split(' ')),
    LCA_ATTR,
    ''.join(LCR_ATTR.split(' ')),
    LCR_ATTR,
    ''.join(REV_ATTR.split(' ')),
    REV_ATTR
)

def cfgKey():
    return myId
    
if __name__ == '__main__':
    #
    # Don't convert to json, because we're going to use it
    #
    print get()
    
    
        
    

    



