#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Python API for the ASN1Scc compiler

    Copyright (c) 2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Based on the ASN.1 Space Certified Compiler from Neuropublic

    Contact: maxime.perrotin@esa.int
"""

import subprocess
import tempfile
import uuid
import os
import distutils.spawn as spawn
import sys
import importlib
import logging
import PySide.QtCore as Qt

LOG = logging.getLogger(__name__)

# global needed to store the imported module and list of modules ever loaded
AST = {}

try:
    from enum import Enum
except ImportError:
    raise ImportError('Enum module not found. use sudo pip install enum34')


__all__ = ['ASN1', 'parse_asn1']
__version__ = '0.1'


class ASN1(Enum):
    ''' Flags used to control the compiler options '''
    NoParameterizedTypes = 1
    NoInnerTypes = 2
    NoConstraintReference = 3
    UniqueEnumeratedNames = 4
    AstOnly = 5


def parse_asn1(*files, **options):
    ''' Call the ASN.1 parser on a number of files, and return the module
        containing the AST '''
    global AST

    ast_version = options.get('ast_version', ASN1.UniqueEnumeratedNames)
    flags = options.get('flags', [ASN1.AstOnly])
    assert isinstance(ast_version, ASN1)
    assert isinstance(flags, list)

    asn1scc_root = os.path.dirname(spawn.find_executable('asn1.exe'))
    tempdir = tempfile.mkdtemp()
    filename = str(uuid.uuid4()).replace('-', '_')
    filepath = tempdir + os.sep + filename + '.py'

    # dump python.stg in the temp directory
    #stg = Qt.QFile(':misc/python.stg')
    #stg_data = stg.readData(stg.size())
    stg = asn1scc_root + os.sep + 'python.stg'
    #with open(tmp_stg, 'w') as fd:
    #    fd.write(stg_data)

    args = ['asn1.exe',
            '-customStgAstVerion', str(ast_version.value),
            '-customStg', stg + ':' + filepath] + list(*files)

    LOG.debug('Calling: ' + ' '.join(args))
    try:
        ret = subprocess.check_call(args)
    except subprocess.CalledProcessError as err:
        LOG.debug(str(err))
        raise TypeError('asn1.exe execution failed')
    sys.path.append(tempdir)
    if ret == 0:
        if filename in AST.viewkeys():
            # Re-import module if it was already loaded
            ast = AST[filename]
            reload(ast)
        else:
            ast = importlib.import_module(filename)
            AST[filename] = ast
        return ast
    else:
        raise TypeError('Error calling ASN.1 compiler')


if __name__ == '__main__':
    try:
        ast = parse_asn1('dataview-uniq.asn',
                          ast_version=ASN1.NoParameterizedTypes,
                          flags=[ASN1.AstOnly])
        print ast.types.keys()
        sys.exit(0)
    except TypeError as err:
        print(str(err))
        sys.exit(1)
