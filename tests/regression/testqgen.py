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
import unittest
import difflib
import re
import string

__version__ = '1.0.0'
LOG = logging.getLogger(__name__)

def parse_args():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser(version=__version__)
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
    
def diff(expected, actual, msg=None, count=1, case_sensitive=True,
         update=None, silent=False, directory=''):
    """Compare EXPECTED and str2. If not equal, display a diff and raise an
       error.
    """
    # try looking in self.directory
    full_expected = os.path.join(directory, expected)

    if isinstance(expected, file):
        str1 = expected.read()
        frm = expected.name
    elif os.path.isfile(expected):
        str1 = file(expected).read()
        frm = expected
    elif os.path.isfile(full_expected):
        expected = full_expected
        str1 = file(expected).read()
        frm = expected
    elif update:
        # Check if it's a valid file path, in which case use it. Because of
        # --update, the file will be created and filled with the expected
        # output further below.
        try:
            file(full_expected, 'w')
            expected = full_expected
            str1 = ''
            frm = expected
        except:
            str1 = expected
            frm = "Expected"
    else:
        str1 = expected
        frm = "Expected"

    if os.path.isfile(actual):
            actual = file(actual).read()
    
    string.replace(actual, "\r", "")

    expected = str1 * count

    diff = colored_unified_diff(
        expected, actual, fromfile=frm, tofile="Output")

    if diff:
        if msg:
            msg = msg + "\n"
        else:
            msg = ""

        msg = msg + "------- EXPECTED: ----\n" \
                + expected + "\n" \
                + "------- ACTUAL: --------\n" + actual + "\n"

        if update:
            # If updating baselines, do not stop at the first difference

            if frm != "Expected":
                f = file(frm, "w")
                f.close()

        else:
            d = re.sub("\n", "$\n", "\n".join(diff))
            if not silent:
                unittest.TestCase.fail(msg + "\n" + d)
            else:
                return msg + "\n" + d

def colored_unified_diff(a, b, fromfile='', tofile='',
                         fromfiledate='', tofiledate='', n=3, lineterm='\n',
                         onequal=None, onreplaceA=None, onreplaceB=None):

    for line in difflib.unified_diff(a, b, fromfile, tofile):
        yield line

def main():         
    options = parse_args()
    init_logging(options)
    
    jar_dir = os.environ.get('JAR_DIR')
    jar_name = os.environ.get('JAR_NAME')
    jar_path = os.path.join (jar_dir,jar_name)

    for file in options.files:
        #expected = file + '.out'
        cmd = ['java', '-jar', jar_path, os.path.abspath(file)]
        print (cmd)
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        errcode = proc.wait()
        #diff(expected=expected, actual=proc.stdout)

    return (errcode, stdout, stderr)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    