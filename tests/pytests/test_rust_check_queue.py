#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Regression tests: the ``<process>_check_queue`` symbol in the Rust backend.

A process with continuous signals needs a ``<process>_check_queue`` function
that tells the generated continuous-signals loop whether a message is pending.

* Standalone (no ``--taste``) nothing else provides that symbol, so the
  generator must emit a stub *definition*.
* Under ``--taste`` the TASTE glue (kazoo's node_linux_interface template)
  defines ``<process>_check_queue`` in C++, polling the function's threads.
  Emitting the stub as well gives the symbol two strong definitions and the
  link fails with::

      multiple definition of `<process>_check_queue'
        lib<process>.a(...)  <- Rust stub
        libdemo.a(demo_interface.o)  <- glue

  so the generator must emit an ``extern "C"`` *declaration* only, keeping
  the call site resolvable while leaving the definition to the glue.

Run with:
    cd tests/pytests && python3 -m pytest test_rust_check_queue.py -v
"""

import os
import shutil
import tempfile

from opengeode import ogParser, RustGenerator


ASN1_CONTENT = """\
DV DEFINITIONS ::=
BEGIN
    MyInteger ::= INTEGER (0 .. 100)
END
"""

# abort_flag is never set by an input, so `transition continuous abort_flag`
# declares a continuous signal: that is what makes the generator emit the
# check_queue service.
MODEL_TEMPLATE = """\
system demo;
    /* CIF TEXT (100, 100), (300, 200) */
    use DV comment '{asn1_path}';

    signal start_sig;
    /* CIF ENDTEXT */

    channel c
        from env to demo with start_sig;
    endchannel;

    block demo;
        signalroute r
            from env to demo with start_sig;
        connect c and r;

        /* CIF PROCESS (200, 100), (150, 75) */
        process demo;
            /* CIF TEXT (50, 50), (300, 200) */
            dcl abort_flag MyInteger := 0;
            dcl counter MyInteger := 0;
            /* CIF ENDTEXT */

            /* CIF START (100, 100), (70, 35) */
            START;
                /* CIF NEXTSTATE (100, 150), (70, 35) */
                NEXTSTATE idle;

            /* CIF state (100, 200), (100, 35) */
            state idle;
                /* CIF input (100, 250), (100, 35) */
                input start_sig;
                    /* CIF NEXTSTATE (100, 300), (70, 35) */
                    NEXTSTATE idle;
                /* CIF provided (300, 200), (150, 35) */
                provided abort_flag = 1;
                    /* CIF task (300, 250), (150, 35) */
                    task counter := counter + 1;
                    /* CIF NEXTSTATE (300, 300), (70, 35) */
                    NEXTSTATE busy;
            endstate;

            /* CIF state (300, 300), (100, 35) */
            state busy;
                /* CIF provided (300, 350), (150, 35) */
                provided abort_flag = 2;
                    /* CIF task (300, 400), (150, 35) */
                    task counter := counter + 1;
                    /* CIF NEXTSTATE (300, 450), (70, 35) */
                    NEXTSTATE idle;
            endstate;
        endprocess demo;
        endblock;
   endsystem;
"""

SYMBOL = 'demo_check_queue'


def _generate(taste):
    '''Generate demo.rs for the model, with or without the TASTE flag'''
    tmpdir = tempfile.mkdtemp(prefix='og_check_queue_')
    asn1_path = os.path.join(tmpdir, 'dv.asn')
    with open(asn1_path, 'w', encoding='utf-8') as f:
        f.write(ASN1_CONTENT)
    pr_path = os.path.join(tmpdir, 'demo.pr')
    with open(pr_path, 'w', encoding='utf-8') as f:
        f.write(MODEL_TEMPLATE.format(asn1_path=asn1_path))

    ast, errors, _warnings = ogParser.parse_pr(files=[pr_path])
    assert not errors, 'Unexpected parse errors: %s' % (errors,)

    cwd = os.getcwd()
    try:
        os.chdir(tmpdir)
        RustGenerator.generate(ast.processes[0], simu=False, taste=taste)
        with open(os.path.join(tmpdir, 'demo.rs'), 'r', encoding='utf-8') as f:
            return f.read()
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_model_has_continuous_signals():
    '''Guard: without continuous signals the test would prove nothing'''
    code = _generate(taste=False)
    assert 'branch_continuous_signals' in code, \
        'model no longer generates continuous-signal code'


def test_standalone_defines_the_stub():
    '''Without --taste the generator must provide the symbol itself'''
    code = _generate(taste=False)
    assert 'pub unsafe extern "C" fn %s(res: &mut bool)' % SYMBOL in code, \
        'standalone build lost its check_queue stub definition'
    assert 'fn %s(res: &mut bool);' % SYMBOL not in code, \
        'standalone build must not merely declare check_queue'


def test_taste_declares_but_does_not_define():
    '''With --taste the glue defines the symbol; we only declare it'''
    code = _generate(taste=True)
    assert 'fn %s(res: &mut bool);' % SYMBOL in code, \
        'TASTE build lost the extern declaration of check_queue'
    assert 'pub unsafe extern "C" fn %s(res: &mut bool)' % SYMBOL not in code, \
        'TASTE build must not define check_queue (duplicate symbol at link)'


def test_taste_still_calls_the_symbol():
    '''The continuous-signals loop must keep calling it in both modes'''
    for taste in (False, True):
        code = _generate(taste=taste)
        assert '%s(&mut message_pending);' % SYMBOL in code, \
            'check_queue call missing (taste=%s)' % taste
