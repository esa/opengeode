#!/usr/bin/env python
from generatorc import Generator

import ogParser
import ogAST

import signal
import sys
import os
import optparse
g_symbols = set()

# nextStatesCoord is used to merge NEXTSTATE and STATE symbol when they have the same coordinates
nextStatesCoord = {}

processName = 'opengeode'

ogDirName = os.path.dirname(os.path.abspath(sys.argv[0])) + '/'

if __name__ == '__main__':
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Parse the command line
    usage = 'usage: generator.py [--verbose] [--open | --check | --toC file.pr]'
    version = '0.1'
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', action='store_true', default=False, help='Display debug information')
    parser.add_option('-t', '--taste',   action='store_true', default=False, help='Generate TASTE related wrappers')
    parser.add_option('-f', '--filename', metavar='file.pr', dest='inputfile', help='File to be used for code generation (.pr extension)')
    parser.add_option('-o', '--outputname', metavar='opengeode', dest='outputname', help='basename for generated code')
    options, args = parser.parse_args()
    ret = 0
    print 'Generating code for', options.inputfile
    process, warnings, errors = ogParser.parseProcessDefinition(fileName=options.inputfile)
    print 'Parsing complete. Summary, found ' + str(len(warnings)) + ' warnings and ' + str(len(errors)) + ' errors'
    for w in warnings:
        print w
    for e in errors:
        print e
    if len(errors) > 0:
        ret = -1
    else:
        generator = Generator(options.outputname, True, options.taste)
        generator.generate(process)

    sys.exit(ret)
