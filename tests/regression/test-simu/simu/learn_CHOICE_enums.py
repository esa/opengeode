#!/usr/bin/env python2
import os
import sys
choices = []
enums = []
bEnum = False

''' Parse the ASN.1-generated header file and extract the constants used for
CHOICE determinants (#define det..._PRESENT) and ENUMERATED values
Emit strings that are appended to DV.py from Makefile.python
There is no name clash thanks to the rename policy of the ASN.1 compiler
(a constant cannot be defined twice)
'''

for line in open(sys.argv[1] + '.h', 'r'):
    if '_PRESENT' in line and not line.startswith('#define'):
        choices.append(line.strip().replace(",", ""))
    elif line.strip().startswith('typedef enum {'):
        bEnum = True
    elif line.strip().startswith('}') and bEnum:
        bEnum = False
    elif bEnum:
        enums.append(line.strip().replace(",", "").split("="))

enums_dump = "\n    ".join(
    'printf("%s = %%d\\n", %s);' % (e, e)
    for e in choices
)

enums_dump += "\n    ".join(
    'printf("%s = %d\\n");' % (name.strip(), int(val))
    for name, val in enums
)
uniq = os.getpid()
extractor_filename = "/tmp/enums_%d" % uniq
f = open(extractor_filename + ".c", 'w')
f.write("""
#include <stdio.h>
#include "%(base)s.h"

void main()
{
%(enums_dump)s
}""" % {"enums_dump": enums_dump, "base": sys.argv[1]})
f.close()
cmd = "gcc -o %s -I. %s.c" % (extractor_filename, extractor_filename)
if os.system(cmd) != 0:
    print("Failed to extract CHOICE enum values...")
    sys.exit(1)
os.system(extractor_filename)
os.unlink(extractor_filename + ".c")
os.unlink(extractor_filename)
