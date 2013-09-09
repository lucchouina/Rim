#!/usr/bin/env python
#
# command.py
#
""" utilities for running commands """

import subprocess
import os
import tempfile

def run_command_lines(c):
    """ run a command as a subprocess, return an array of lines.
    
    The newlines are stripped from the representation
    """
    child = subprocess.Popen(c, stdout=subprocess.PIPE, shell=True)
    results = child.communicate()
    return results[0].strip('\n').split('\n')


def run_command_one_line(c):
    """ run a command, and assume only the first returned line has value """    
    return run_command_lines(c)[0]
    

def run_command(c):
    """ run a command, don't expect anything back """
    run_command_one_line(c)


def replace_in_file(filename, oldString, newString, word=False):
    """ routine to replace a string in a file """
    if os.path.exists(filename) == False:
        return
        
    tmpfileName = tempfile.mkstemp()[1]
    
    if word:
        run_command("sed -i -e 's/\<%s\>/%s/g' %s" % ( oldString, newString, filename))
    else:
        run_command("sed -i -e 's/%s/%s/g' %s" % ( oldString, newString, filename))
            

def replace_line_in_file(filename, matchString, replacement):
    """ routine to replace a line in a file """
    if os.path.exists(filename) == False:
        return
    run_command("sed -i -e 's^.*%s.*^%s^' %s" % (matchString, replacement, filename))
            
        

