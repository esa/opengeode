#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Run some tests using QGen components
"""

import os
import sys
import logging
import argparse
import subprocess
__version__ = '1.0.0'
LOG = logging.getLogger(__name__)

def parse_args():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument('rule', metavar='Rule', type=str)
    parser.add_argument('files', metavar='file.pr', type=str, nargs='*',
            help='SDL file(s)') 
    parser.add_argument('-u', '--update', action='store_true')
    
    return parser.parse_args()             

def init_logging(options):
    ''' Initialize logging '''
    terminal_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(terminal_formatter)
    LOG.addHandler(handler_console)

def getSizeFiles(list,size):
    err = 0
    files = [os.path.abspath(file) for file in list]
    for file in files:
        s = os.path.getsize(file)
        if s > size:
            err = 1
            LOG.error(file+ " too large - size " + str(s))
        else:
            LOG.warning(file+ " size " + str(s))

    return err
    
def main():         
    options = parse_args()
    init_logging(options)
    files=''
    
    for file in options.files:
       files = files + file + ' '
       
    cmd = ['make ', files, ' --check']
    
    print (cmd)
    proc = subprocess.Popen(
      cmd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
        
    stdout, stderr = proc.communicate()
    errcode = proc.wait()
    return (errcode, stdout, stderr)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
