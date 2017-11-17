#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run some tests using QGen components
"""

from string import Template
import os
import sys
import logging
import argparse
import subprocess
import unittest
import difflib
import re
import string
import time
import test

LOG = logging.getLogger(__name__)

def parse_args():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument('rule', metavar='Rule', type=str)
    parser.add_argument('root_model', metavar='file.pr', type=str,
            help='SDL root model') 
    parser.add_argument('-u', '--update', action='store_true')
    
    return parser.parse_args()             

def init_logging(options):
    ''' Initialize logging '''
    terminal_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(terminal_formatter)
    LOG.addHandler(handler_console)
    
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
    start = time.time()
    results = []
    op = parse_args()
    init_logging(op)

    result = run_test(op)
    print("%40s: %s" % (result[3], test.colorMe(result[0],
          '[OK]' if result[0]==0 else '[FAILED]')))
    results.append(result)
    sys.stdout.write('\n')

    elapsed = time.time() - start
    return test.summarize(results, elapsed)

def run_test(op):
    ''' Call a SDL parser with the required arguments '''

    jar_dir = os.environ.get('JAR_DIR')
    jar_name = os.environ.get('JAR_NAME')
    jar_path = os.path.join (jar_dir,jar_name)
    
    asntest = False
    
    if op.rule == 'test-qgen-parse':
        lang = 'xmi'
    elif op.rule == 'test-qgen-ada':
        lang = 'ada'
    elif op.rule == 'test-qgen-c':
        lang = 'c'
    elif op.rule == 'test-qgen-c-asn':
        asntest = True
        lang = 'c'
    elif op.rule == 'test-qgen-ada-asn':
        asntest = True
        lang = 'ada'
    else:
        # the importer crashes if any other value us used here,
        # for now keep xmi as default value
        lang = 'xmi'
    
    #expected = file + '.out'
    if asntest:
        asn_call = ['asn1.exe', 'dataview-uniq.asn']
        p0 = subprocess.Popen(asn_call,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        stdout, stderr = p0.communicate()
        errcode = p0.wait()

        if errcode != 0:
            return (errcode, stdout, stderr, op.root_model, op.rule)
        
        cmd = ['java', '-jar', jar_path, op.root_model,
               '--language', lang,
               '--output', 'generated_asn_' + lang]
    else:
        cmd = ['java', '-jar', jar_path, op.root_model,
               '--language', lang, '--generate-types',
               '--output', 'generated_' + lang,
               '--type-prefix', 'asn1QGen']
           
    p1 = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    errcode = p1.wait()

    if errcode != 0:
        return (errcode, stdout, stderr, op.root_model, op.rule)

    #diff(expected=expected, actual=proc.stdout

    if lang in ('ada', 'c'):
        p2 = _compile (lang)
        stdout, stderr = p2.communicate()
        errcode = p2.wait()
    
    return (errcode, stdout, stderr, op.root_model, op.rule)

def _run_gprbuild(gprfile):
    args = ["gprbuild",
            "-p",   # Create obj dirs
            "-j1",  # when tests run in parallel, CPUs are already
            # being used by other tests.
            "-k",   # Do not stop on first error
            "-P%s" % gprfile,
            "-gnatwa", "-gnatyg-dm", "-gnateE"]

    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT)
    return proc

def _compile (lang):
    source_dirs = '"."'
    main_file = ""
    compiler_pkg = ""
    linker_pkg = ""
    binder_pkg = ""
    do_c = lang == "c"
    do_ada = lang == "ada"
    c_prj = ""
    ada_prj = ""

    src_path = 'generated_' + lang

    flags = ''
    c_std = 'c99'

    languages = """for Languages use ({0});"""

    compiler_pkg = """package Compiler is
  for Default_Switches ("{0}") use ("-g"{1});
end Compiler;"""
    linker_pkg = """package Linker is
  for Default_Switches ("{0}") use ("-lm");
end Linker;"""
    binder_pkg = """package Binder is
  for Default_Switches ("{0}") use ("-E");
end Binder;"""

    template_ada = Template("""with "Prj_C";

project Prj_Ada is
   for Source_Dirs use (${source_dirs});
   for Object_Dir use "obj_ada";
   for Exec_Dir use "exec";
   ${main}
   ${lang}
   ${compiler_pkg}
   ${linker_pkg}
   ${binder_pkg}
end Prj_Ada;""")
    ada_prj = template_ada.substitute(
        source_dirs=source_dirs,
        main=main_file.format("main.adb"),
        lang=languages.format('"Ada"'),
        compiler_pkg=compiler_pkg.format(
            "Ada", ', "-gnata"%s' % flags),
        linker_pkg=linker_pkg.format("Ada"),
        binder_pkg=binder_pkg.format("Ada"))
    gpr_filename_ada = os.path.join(src_path, 'Prj_Ada.gpr')
    with open(gpr_filename_ada, 'w') as f:
        f.write(ada_prj)

    template_c = Template("""project Prj_C is
   for Source_Dirs use (${source_dirs});
   for Object_Dir use "obj";
   for Exec_Dir use "exec";
   ${main}
   ${lang}
   ${compiler_pkg}
   ${linker_pkg}
   ${binder_pkg}
end Prj_C;""")
    c_prj = template_c.substitute(
        source_dirs=source_dirs,
        main=main_file.format("main.c"), lang=languages.format('"C"'),
        compiler_pkg=compiler_pkg.format("C", ', "-std=%s"%s' %
                                         (c_std, flags)),
        linker_pkg=linker_pkg.format("C"),
        binder_pkg=binder_pkg.format("C"))
    gpr_filename_c = os.path.join(src_path, 'Prj_C.gpr')
    with open(gpr_filename_c, 'w') as f:
        f.write(c_prj)

    if do_ada:
        return _run_gprbuild(gpr_filename_ada)
    if do_c:
        return _run_gprbuild(gpr_filename_c)
            
if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
    