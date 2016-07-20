#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Python API for the ASN1Scc compiler

    Copyright (c) 2013-2016 European Space Agency

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
terminal_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
handler_console = logging.StreamHandler()
handler_console.setFormatter(terminal_formatter)
LOG.addHandler(handler_console)

# global needed to store the imported module and list of modules ever loaded
AST = {}
# Same for the modules imported by the call to asn2DataModel
ASN2DM = {}

try:
    from enum import Enum
except ImportError:
    raise ImportError('Enum module not found. Run pip install --user enum34')


__all__ = ['ASN1', 'parse_asn1']


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

def waitfor_qprocess(qprocess, name):
    ''' Wait the the execution of a QProcess instance
    Raise an exception if anything went wrong, otherwise return stdout '''
    if not qprocess.waitForStarted():
        raise TypeError('Could not start ' + name)
    if not qprocess.waitForFinished():
        raise TypeError('Execution time out : ' + name)
    exitcode = qprocess.exitCode()
    err = qprocess.readAllStandardError()
    std = qprocess.readAllStandardOutput()
    if exitcode != 0:
        raise TypeError(name + ' error (exit code = {}) - {}'
                        .format(exitcode, str(err)))
    return std


def parse_asn1(*files, **options):
    ''' Call the ASN.1 parser on a number of files, and return the module
        containing the AST
        This function uses QProcess to launch the ASN.1 compiler because
        the subprocess module from Python has issues on the Windows platform
    '''
    ast_version = options.get('ast_version', ASN1.UniqueEnumeratedNames)
    rename_policy = options.get('rename_policy', ASN1.NoRename)
    flags = options.get('flags', [ASN1.AstOnly])
    assert isinstance(ast_version, ASN1)
    assert isinstance(rename_policy, ASN1)
    assert isinstance(flags, list)
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

    _ = waitfor_qprocess(asn1scc, "ASN.1 Compiler")

    if filename in AST.viewkeys():
        # Re-import module if it was already loaded
        ast = AST[filename]
        reload(ast)
    else:
        ast = importlib.import_module(filename)
        AST[filename] = ast
    return ast


def asn2dataModel(*files):
    ''' Call asn1DataModel, including the Makefile.python and return
    the imported module "name_of_dataview_asn.py"
    From this module it is possible to create native Asn1scc instances of
    ASN.1 data types, and to access to DV.py, which contains constants
    such as the _PRESENT fields for choice selectors '''
    assert len(files) > 0

    # 1) Create a temporary directory for the output
    tempdir = tempfile.mkdtemp()
    sys.path.insert(0, tempdir)
    # Use a unique name for the asn1 concatenated module
    concat_prefix = str(uuid.uuid4()).replace('-', '_')
    concat_path = os.path.join(tempdir, concat_prefix)

    # 2) Concat all input files to the output directory
    cat_bin = spawn.find_executable('cat')
    args = list(files)
    cat = QProcess()
    LOG.debug(os.getcwd())
    LOG.debug(cat_bin + ' ' + ' '.join(args))
    cat.start(cat_bin, args)
    merged = waitfor_qprocess(cat, 'Merge dataviews')
    with open(concat_path + '.asn', 'wt') as merged_file:
        merged_file.write(merged)

    # 3) Run asn2dataModel
    asn2dm_bin = spawn.find_executable('asn2dataModel')
    args = ['-toPython', '-o', tempdir, concat_path + '.asn']
    asn2dm = QProcess()
    LOG.debug(os.getcwd())
    LOG.debug(asn2dm_bin + ' ' + ' '.join(args))
    asn2dm.start(asn2dm_bin, args)
    waitfor_qprocess(asn2dm, 'DMT tool "asn2dataModel"')

    # 4) call make -f Makefile.python to build the .so
    make_bin = spawn.find_executable('make')
    args = ['-f', 'Makefile.python']
    make = QProcess()
    make.setWorkingDirectory(tempdir)
    LOG.debug(os.getcwd())
    LOG.debug(make_bin + ' ' + ' '.join(args))
    make.start(make_bin, args)
    waitfor_qprocess(make, 'make -f Makefile.python')

    if concat_prefix in ASN2DM.viewkeys():
        # Re-import module if it was already loaded
        asn1mod = ASN2DM[concat_prefix]
        reload(asn1mod)
        reload(asn1mod.DV)
        import Stubs
        reload(Stubs)
    else:
        asn1mod = importlib.import_module(concat_prefix + '_asn')
        # force reload of modules in case of multiple calls
        reload(asn1mod.DV)
        import Stubs
        reload(Stubs)
        ASN2DM[concat_prefix] = asn1mod
    sys.path.pop(0)
    return asn1mod


if __name__ == '__main__':
    LOG.setLevel(logging.DEBUG)
    try:
        ast = parse_asn1('dataview-uniq.asn',
                          ast_version=ASN1.NoParameterizedTypes,
                          flags=[ASN1.AstOnly])
        print ast.types.keys()
        sys.exit(0)
    except TypeError as err:
        print(str(err))
        sys.exit(1)
