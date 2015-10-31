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
from PySide.QtCore import QProcess


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
    NoRename = 0
    RenameOnlyConflicting = 1
    RenameAllEnumerants = 2


def parse_asn1(*files, **options):
    ''' Call the ASN.1 parser on a number of files, and return the module
        containing the AST
        This function uses QProcess to launch the ASN.1 compiler because
        the subprocess module from Python has issues on the Windows platform
    '''
    global AST

    ast_version = options.get('ast_version', ASN1.UniqueEnumeratedNames)
    rename_policy = options.get('rename_policy', ASN1.NoRename)
    flags = options.get('flags', [ASN1.AstOnly])
    assert isinstance(ast_version, ASN1)
    assert isinstance(rename_policy, ASN1)
    assert isinstance(flags, list)
    #if os.name == 'posix' and hasattr(sys, 'frozen'):
        # Frozen Linux binaries are expected to use the frozen ASN.1 compiler
        # No: there are issues with freezing the .NET applications - discard
    #     asn1exe = 'asn1scc'
    #else:
    #    asn1exe = 'asn1.exe'
    path_to_asn1scc = spawn.find_executable('asn1.exe')

    if not path_to_asn1scc:
        raise TypeError('ASN.1 Compiler not found in path')
    if os.name == 'posix':
        path_to_mono = spawn.find_executable('mono')
        if not path_to_mono:
            raise TypeErorr('"mono" not found in path. Please install it.')
        binary = path_to_mono
        arg0 = path_to_asn1scc
    else:
        binary = path_to_asn1scc
        arg0 = ''
    asn1scc_root = os.path.abspath(os.path.dirname(path_to_asn1scc))
    # Create a temporary directory to store dataview.py and import it
    tempdir = tempfile.mkdtemp()
    sys.path.append(tempdir)
    if os.name == 'nt':
        # On windows, remove the drive letter, workaround to ASN1SCC bug
        tempdir = tempdir[2:]
        asn1scc_root = asn1scc_root[2:]
    filename = str(uuid.uuid4()).replace('-', '_')
    filepath = tempdir + os.sep + filename + '.py'

    stg = asn1scc_root + os.sep + 'python.stg'

    args = [arg0, '-customStgAstVerion', str(ast_version.value),
            '-customStg', stg + '::' + filepath,
            '-renamePolicy', str(rename_policy.value)] + list(*files)
    asn1scc = QProcess()
    LOG.debug(os.getcwd())
    LOG.debug(binary + ' ' + ' '.join(args))
    asn1scc.start(binary, args)
    if not asn1scc.waitForStarted():
        raise TypeError('Could not start ASN.1 Compiler')
    if not asn1scc.waitForFinished():
        raise TypeError('Execution of ASN.1 Compiler timed out')
    exitcode = asn1scc.exitCode()
    result = asn1scc.readAllStandardError()
    if exitcode != 0:
        raise TypeError('ASN.1 Compiler Error (exit code = {}) - {}'
                        .format(exitcode, str(result)))
    else:
        if filename in AST.viewkeys():
            # Re-import module if it was already loaded
            ast = AST[filename]
            reload(ast)
        else:
            ast = importlib.import_module(filename)
            AST[filename] = ast
        return ast


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
