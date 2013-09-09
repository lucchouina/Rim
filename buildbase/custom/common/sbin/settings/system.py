#!/usr/bin/env python
#

""" system.py

Class that encapsulates access to various system settings.
"""

import simplejson as json
from settings.utils import *
import imp
import glob
import sys

ROOT_ATTR="root"

ALL_ATTRS=[ROOT_ATTR ]

def attrChanged(old, new, schema):
    for attr in old:
        # check if this is a read-only or write-only attrbute
        # and do not flag a change if it is.
        if schema[attr].has_key("access") and schema[attr]["access"] == "read-only": continue
        if new.has_key(attr) and old[attr] != new[attr]:
            return True
    return False

def attrChangeNotify(old, new, key, nattr, callback, tracker=[]):
    for attr in old[key]:
        if old[key][attr] != new[key][attr] and ( nattr == None or len(nattr) == 0 or attr in nattr):
            if callback not in tracker:
                tracker.append(callback)
                return callback(old, new)
    return ""

def attrNotify(old, new, key, interests, tracker=[]):
    s=""
    for party in interests:
        callbacks=interests[party]
        for callback in callbacks:
            attrs=callbacks[callback]
            for attr in attrs:
                if len(attr) == 0 or attr == key :
                    si=attrChangeNotify(old, new, key, attrs[attr], callback, tracker)
                    if len(si) > 0:
                        si="\n#\n# notification '%s'\n#\n%s\n" % (party, si)
                    s+=si;
    return s;

def printErrors(errors, keys=[]):
    for key in errors:
        if isinstance(errors[key], dict):
            keys.append(key)
            printErrors(errors[key], keys)
            keys.pop()
        elif len(errors[key]):
            keys.append(key)
            for k in keys:
                print "%s:" % k,
            print errors[key]
            keys.pop()

def prootkeys(root):
    print "Available categories are :"
    for key in sorted(root):
        print "   %s" % key
        
#     
# extract a simple list of configuration group keys
# form a json returned from getSystemInfo
#
def getkeys(root):
    return [k for k in root]

#
# the presonality of this node is coming this single boot option
# Else, it has no personality yet! Needs to glow up and get one!
#
def nodeName():
    cmdline=open("/proc/cmdline","r").readline()
    assignments=cmdline.split()
    for assignment in assignments:
        items=assignment.split("=")
        if len(items) > 1:
            if items[0]=="rim_node":
                return items[1]
    return ""
       
def get_schema(root, handlers):
    #
    # construct the schema from the handlers
    schemaStr=""
    for key in sorted(root):
        if handlers.has_key(key) and hasattr(handlers[key], "schema"):
            s= handlers[key].schema()
            if len(schemaStr) > 0:
                schemaStr='%s,\n%s' % (schemaStr, s)
            else:
                schemaStr=s

    schemaStr="""
    {
    "type":"map",
    "title":"Rim %s Startup Configuration",
    "mapping":
        {
    %s
        }
    }
    """ % (nodeName(), schemaStr)
    return json.loads(schemaStr)
   
def lineCol(msg):
    msg=str(msg)
    try:
        line=str(msg).index("line ")
        col=msg.index("column ")
        par=msg.index("(")
        return int(msg[line+4:col-1]), int(msg[col+7:par-1])
    except:
        raise
        return None, None

def get_systeminfo(keys):
    """ retrieve all system settings """
    root = {}
    handlers = {}
    interests = {}
    notFound = [ k for k in keys ]
    fullList=[]
    for infile in sorted(glob.glob('%s/settings/handlers/*.py' % sys.path[0])):
    
        # skip over any python package management files
        if os.path.basename(infile)[0:2] == "__": continue
        
        fname = os.path.basename(infile)[:-3]
        mod=imp.load_source(fname, infile) 
        key=mod.cfgKey()
        fullList.append(key)
        handlers[key]=mod
        if not len(keys) or key in keys: 
            if 'get' in dir(mod):
                if not len(keys): 
                    try:
                        sstr=mod.schema()
                        schema=json.loads("{%s}" % sstr)[key]
                    except ValueError as msg:
                        linerr, col = lineCol(msg)
                        if linerr:
                            print "Error processing schema '%s' %d:%d : '%s'" % (key, linerr, col, msg)
                            print "Schema follows:" 
                            lineno=0
                            for line in sstr.split("\n"):
                                lineno=lineno+1
                                print line
                                if lineno==linerr:
                                    print "%*s%s" % (col-1, "", "^<<<<<< ------------ %s ------------- <<<<<" % msg)
                        else:
                            raise msg
                    except:
                        raise
                else: 
                    notFound.remove(key)
                    schema={}
                if not schema.has_key("hidden") or schema["hidden"] == "false":
                    list=mod.get()
                    if len(list) > 0:
                        root[key]=list
            if 'interests' in dir(mod):
                interests[key]=mod.interests()

    if len(notFound):
       print "Configuration block not found for item(s) '%s'\n" % notFound
       prootkeys(fullList);

    return handlers, interests, root, get_schema(root, handlers)

####################################################
#
#  Validation functions
#
####################################################

# a forAllValues callback to perform syntax validation
def validateSyntax(value, schema, name, errors):
    if schema.has_key('subtype'): tkey='subtype'
    else: tkey='type'
    if not schema.has_key('required') or not schema['required']:
        if schema['type'] == 'str' and not len(value) :
            return True
        if schema['type'] == 'int' and value == -1 :
            return True
    valStr="validate_%s" % schema[tkey]
    if globals().has_key(valStr): return globals()[valStr](value, name, errors)
    return True

# a forAllValues callback to perform syntax validation
def validateRequired(value, schema, validateKey):
    isIn=True
    if len(validateKey) and schema.has_key(validateKey): isIn=schema[validateKey]
    if schema.has_key('required'): isReq=schema['required']
    else: isReq=False
    if isIn and isReq:
        type=schema['type']
        if ( type == "int" and value == -1) or ( type == "str" and len(value) == 0 ):
            return "Entry is required"
    return ""

def validate(values, schema, handlers, validateKey, errors):
    foundErrors=False
    for key in values:
        # depth first
        if isinstance(values[key], dict):
            errors[key]={}
            if schema[key].has_key('mapping'): mapkey='mapping'
            if schema[key].has_key('items'): mapkey='items'
            if schema[key].has_key('sequence'): mapkey='sequence'
            if validate(values[key], schema[key][mapkey], handlers, validateKey, errors[key]):
                foundErrors=True
            # if the leaves have no errors, we run the validation hook for the group
            else:
                if handlers.has_key(key):
                    mod=handlers[key]
                    if 'validate' in dir(mod) and not mod.validate(values[key], key, errors):
                        foundErrors=True
            if not foundErrors:
                del errors[key]
                
        else:
            # single value check requirements and syntax
            msg=validateRequired(values[key], schema[key], validateKey)
            if len(msg):
                foundErrors=True
                errors[key]=msg
            # then check syntax
            if not validateSyntax(values[key], schema[key], key, errors):
                foundErrors=True
    return foundErrors
    
#
# Test a group of variables. The group to be tested is supplied on the values array
# It is assumed that the ocnfiguration is active and thus all values are syntactly valid
# and the groups as a whole also have been validated.
#
def test(values, schema, handlers, validateKey, errors):
    foundErrors=False
    for key in values:
        # depth first
        if isinstance(values[key], dict):
            mod=handlers[key]
            if 'test' in dir(mod) and not mod.test(values[key], key, errors):
                foundErrors=True
                
    return foundErrors
    
#
# Add/Revove handler - called form the web interface
# CLI has a built in handler for adding items to a sequence.
#
def execOp(root, op, elems):
    handlers, interests, curroot, schema = get_systeminfo([])
    key=elems[0]
    if elems[0] in handlers:
        mod=handlers[key]
        if 'op' in dir(mod):
            return mod.op(root, op, elems[1:])
        else:
            print "Handler for '%s' does not define a 'op' function!!" % key
    else:
        print "Invalid execOp id '%s' - no handler!!" % key
        
    
    

def set_systeminfo(new, exe=True, forced=False, validateKey=""):
    """ set system settings (top level function) """
    
    # log input output and commands to /tmp files
    fprefix='/tmp/setSysConfig'
    
    handlers, interests, old, schema = get_systeminfo([])
    
    logf=open("%s.input" % fprefix, "w")
    logf.write("Old config\n=======\n")
    logf.write(json.dumps(old, sort_keys=True, indent=4))
    logf.write("\nNew config\n=======\n")
    logf.write(json.dumps(new, sort_keys=True, indent=4))
    logf.close()
    
    # for partial input ex: echo '{"WebInfo":{"Port":80}}' | setSystemInfo -n
    # we have to pad the input for proper validation
    for handler in handlers:
        if new.has_key(handler):
            for attr in old[handler]:
                if not new[handler].has_key(attr):
                    new[handler][attr]=old[handler][attr]
        elif old.has_key(handler):
            new[handler]=old[handler]
            
    #
    # perform the validation of the new values
    if not forced:
        errors={}
        foundErrors=validate(new, schema['mapping'], handlers, validateKey, errors)
        if foundErrors:
            return errors, foundErrors
    
    sstr="#!/bin/bash\nexec 2>%s.out 1>&2\nsleep 2\n" % fprefix
    # make sure we call the intereste handlers only once.
    tracker=[]
    for handler in handlers:
        if new.has_key(handler) and (forced or attrChanged(old[handler], new[handler], schema['mapping'][handler]['mapping'])):
            s = handlers[handler].set(old, new)
            if s:
                sstr = "%s\n#\n# handler '%s'\n#\n%s\n" % (sstr, handler, s)

            # check for interest and send notifications
            s = attrNotify(old, new, handler, interests, tracker);
            if s:
                sstr += s

    # we execute the result of the changes via a cron/at job.
    # so that we are garantied that the impact of network (and other) changes will not
    # ripple through and suspend or kill out current session.
    #
    # Each set() will return the impactful commands, ex: /etc/init.d/network restart
    #
    if exe:
        shname="%s.sh" % fprefix
        open(shname, "w").write(sstr)
        fname="%s.filtered" % fprefix
        run_command("rcfilter < %s > %s" % (shname, fname));
        run_command("/usr/bin/at -qb now < %s 1>/dev/null 2>&1" % fname);
    
    return {}, False


if __name__ == '__main__':
    print json.dumps(get_systeminfo())
