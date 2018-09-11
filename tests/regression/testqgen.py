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
import shutil
import glob

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
    ''' Call SDL importer with the required arguments '''

    sdl_importer_launcher = "qgen-sdl"

    gentypes = False
    lang=''
    asnlang=''
    asn_path=''

    if op.rule == 'test-qgen-parse':
        lang = 'xmi_ada'
    elif op.rule == 'test-qgen-ada':
        lang = 'ada'
        asnlang = '-Ada'
    elif op.rule == 'test-qgen-c':
        lang = 'c'
        asnlang = '-c'
    elif op.rule == 'test-qgen-gt-ada':
        gentypes = True
        lang = 'ada'
    elif op.rule == 'test-qgen-gt-c':
        gentypes = True
        lang = 'c'
    else:
        # the importer crashes if any other value us used here,
        # for now keep xmi as default value
        lang = 'xmi'

    if gentypes:
        outfolder = 'generated_gt_' + lang
        cmd = [sdl_importer_launcher,
               '--language', lang, '--generate-types',
               '--output', outfolder,
               '--type-prefix', 'asn1QGen', op.root_model]
    else:
        outfolder = 'generated_' + lang
        cmd = [sdl_importer_launcher,
               '--language', lang,
               '--output', outfolder,
               '--type-prefix', 'asn1Scc', op.root_model]

    if os.path.exists(outfolder):
            shutil.rmtree(outfolder, ignore_errors=True)

    p1 = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    errcode = p1.wait()

    if errcode != 0:
        return (errcode, stdout, stderr, op.root_model, op.rule)

    if not gentypes:
        asn_files = glob.glob ('*.asn')
        if asn_files:
            asn_call = ['asn1.exe', "-equal", '-o', outfolder, asnlang,
                '--type-prefix', 'asn1Scc'] + asn_files

            p0 = subprocess.Popen(asn_call,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            stdout, stderr = p0.communicate()
            errcode = p0.wait()

            if errcode != 0:
                return (errcode, stdout, stderr, op.root_model, op.rule)

            if op.rule == 'test-qgen-ada' and os.path.isfile ("test_qgen_ada.c"):
                asn_call = ['asn1.exe', "-equal", '-o', outfolder, "-c",
                '--type-prefix', 'asn1Scc'] + asn_files
                p0 = subprocess.Popen(asn_call,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                stdout, stderr = p0.communicate()
                errcode = p0.wait()
                if errcode != 0:
                    return (errcode, stdout, stderr, op.root_model, op.rule)

    if lang in ('ada', 'c'):
        errcode, stdout, stderr = _compile (lang, outfolder, gentypes)

    return (errcode, stdout, stderr, op.root_model, op.rule)

def _run_gprbuild(gprfile, exec_file):
    args = ["gprbuild",
            "-p",   # Create obj dirs
            "-j1",  # when tests run in parallel, CPUs are already
            # being used by other tests.
            "-k",   # Do not stop on first error
            "-P%s" % gprfile,
            "-gnatyg-dm", "-gnateE"]

    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    errcode = proc.wait()
    if errcode != 0:
        return (errcode, stdout, stderr)

    if os.path.isfile (exec_file):
        actual = open("actual","w+")
        p = subprocess.Popen (exec_file, stdout=actual,
                   stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        errcode = p.wait()

        if errcode != 0:
            return (errcode, stdout, stderr)

        if os.path.isfile ("expected"):
            errcode = os.system ("diff expected actual")

        return (errcode, stdout, stderr)
    
    return (errcode, stdout, stderr)

def _compile (lang, src_path, gentypes):

    if gentypes:
        c_executable = "test_qgen_gt_c"
        ada_executable = "test_qgen_gt_ada"
    else:
        c_executable = "test_qgen_c"
        ada_executable = "test_qgen_ada"
    c_main = c_executable + ".c"
    ada_main = ada_executable + ".c"
    main_file = ""
    ada_exe_path = ""
    c_exe_path = ""
    do_ada = False
    do_c = False

    if lang == "c":
        do_c = True
        if os.path.isfile (c_main):
            main_file = """for main use ("%s");"""% c_main
            shutil.copy (c_main, src_path)
            c_exe_path = os.path.join(src_path, "exec", c_executable)
    
    if lang == "ada":
        do_ada = True
        if os.path.isfile (ada_main):
            main_file = """for main use ("%s");"""% ada_main
            shutil.copy (ada_main, src_path)
            ada_exe_path = os.path.join(src_path, "exec", ada_executable)

    source_dirs = '"."'
    compiler_pkg = ""
    linker_pkg = ""
    binder_pkg = ""
    c_prj = ""
    ada_prj = ""

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
        main=main_file,
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
        main=main_file, lang=languages.format('"C"'),
        compiler_pkg=compiler_pkg.format("C", ', "-std=%s"%s' %
                                         (c_std, flags)),
        linker_pkg=linker_pkg.format("C"),
        binder_pkg=binder_pkg.format("C"))
    gpr_filename_c = os.path.join(src_path, 'Prj_C.gpr')
    with open(gpr_filename_c, 'w') as f:
        f.write(c_prj)

    if do_ada:
        return _run_gprbuild(gpr_filename_ada, ada_exe_path)
    if do_c:
        return _run_gprbuild(gpr_filename_c, c_exe_path)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
