#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for the SDL Z.100 `select if (...) ... endselect;` construct."""

import os
import tempfile
import shutil
import types

from opengeode import ogParser, AdaGenerator, CGenerator, RustGenerator


ASN1_CONTENT = """\
DV DEFINITIONS ::=
BEGIN
    MyInteger ::= INTEGER (0 .. 100)
    SomeBool ::= BOOLEAN

    feat-enabled BOOLEAN ::= TRUE
    feat-disabled BOOLEAN ::= FALSE
END
"""


MODEL_TEMPLATE = """\
system demo;
    /* CIF TEXT (100, 100), (300, 200) */
    use DV comment '{asn1_path}';

    signal keep_sig;
    signal always_sig(MyInteger);

    select if (feat_enabled);
        signal sig_enabled(MyInteger);
        exported procedure exp_enabled; referenced;
    endselect;

    select if (feat_disabled);
        signal sig_disabled(MyInteger);
        signal sig_multi_disabled;
        signal sig_both_off_1;
        signal sig_both_off_2;
        exported procedure exp_disabled; referenced;
    endselect;
    /* CIF ENDTEXT */

    channel c
        from env to demo with keep_sig, always_sig, sig_enabled, sig_disabled, sig_multi_disabled, sig_both_off_1, sig_both_off_2;
    endchannel;

    block demo;
        signalroute r
            from env to demo with keep_sig, always_sig, sig_enabled, sig_disabled, sig_multi_disabled, sig_both_off_1, sig_both_off_2;
        connect c and r;

        /* CIF PROCESS (200, 100), (150, 75) */
        process demo;
            /* CIF TEXT (50, 50), (300, 200) */
            synonym local_true SomeBool = true;
            synonym local_false SomeBool = false;

            dcl x MyInteger := 0;
            timer keep_timer;

            select if (local_true);
                procedure helper_enabled; referenced;
                timer timer_enabled;
                select if (not local_true);
                    procedure nested_disabled; referenced;
                endselect;
            endselect;

            select if (local_false);
                procedure helper_disabled; referenced;
                timer timer_disabled, timer_multi_disabled;
            endselect;
            /* CIF ENDTEXT */

            /* CIF PROCEDURE (100, 200), (100, 35) */
            procedure exp_enabled;
                START;
                    task x := 1;
                    return;
            endprocedure;

            /* CIF PROCEDURE (100, 250), (100, 35) */
            procedure exp_disabled;
                START;
                    task x := 99;
                    return;
            endprocedure;

            /* CIF PROCEDURE (100, 300), (100, 35) */
            procedure helper_enabled;
                START;
                    task x := 2;
                    return;
            endprocedure;

            /* CIF PROCEDURE (100, 350), (100, 35) */
            procedure helper_disabled;
                START;
                    task x := 98;
                    return;
            endprocedure;

            /* CIF PROCEDURE (100, 400), (100, 35) */
            procedure nested_disabled;
                START;
                    task x := 94;
                    return;
            endprocedure;

            START;
                NEXTSTATE wait;

            state wait;
                input sig_enabled(x);
                    call helper_enabled;
                    NEXTSTATE wait;

                input sig_disabled(x);
                    call helper_disabled;
                    NEXTSTATE wait;

                input sig_multi_disabled, keep_sig;
                    task x := 10;
                    NEXTSTATE wait;

                input sig_both_off_1, sig_both_off_2;
                    task x := 97;
                    NEXTSTATE wait;

                input exp_enabled;
                    task x := 3;
                    NEXTSTATE wait;

                input exp_disabled;
                    task x := 96;
                    NEXTSTATE wait;

                input timer_enabled;
                    task x := 4;
                    NEXTSTATE wait;

                input timer_disabled;
                    task x := 95;
                    NEXTSTATE wait;

                input timer_multi_disabled, keep_timer;
                    task x := 11;
                    NEXTSTATE wait;
            endstate;
        endprocess demo;
    endblock;
endsystem;
"""


def _parse_model():
    tmpdir = tempfile.mkdtemp(prefix="og_select_if_")
    try:
        ogParser.USER_DEFINED_TYPES.clear()
        asn1_path = os.path.join(tmpdir, "dataview.asn")
        with open(asn1_path, "w", encoding="utf-8") as f:
            f.write(ASN1_CONTENT)
        pr_text = MODEL_TEMPLATE.format(asn1_path=asn1_path)
        pr_path = os.path.join(tmpdir, "demo.pr")
        with open(pr_path, "w", encoding="utf-8") as f:
            f.write(pr_text)
        ast, warnings, errors = ogParser.parse_pr(files=[pr_path])
        return ast, errors, warnings, tmpdir
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def test_select_if_ast_pruning():
    ast, errors, warnings, tmpdir = _parse_model()
    try:
        assert not errors, f"Unexpected parse errors: {errors}"
        assert len(ast.select_if) == 5

        proc = ast.processes[0]
        in_sig_names = {s["name"].lower() for s in proc.input_signals}
        assert "keep_sig" in in_sig_names
        assert "always_sig" in in_sig_names
        assert "sig_enabled" in in_sig_names
        assert "exp_enabled" in in_sig_names
        assert "sig_disabled" not in in_sig_names
        assert "sig_multi_disabled" not in in_sig_names
        assert "sig_both_off_1" not in in_sig_names
        assert "sig_both_off_2" not in in_sig_names
        assert "exp_disabled" not in in_sig_names

        # Check timers
        timer_names = {t.lower() for t in proc.timers}
        assert "keep_timer" in timer_names
        assert "timer_enabled" in timer_names
        assert "timer_disabled" not in timer_names

        # Check procedures (both declarations and definitions)
        proc_names = {p.inputString.lower() for p in proc.procedures}
        inner_proc_names = {p.inputString.lower() for p in proc.content.inner_procedures}
        assert "exp_enabled" in proc_names
        assert "helper_enabled" in proc_names
        assert "exp_enabled" in inner_proc_names
        assert "helper_enabled" in inner_proc_names
        assert "exp_disabled" not in proc_names
        assert "helper_disabled" not in proc_names
        assert "nested_disabled" not in proc_names
        assert "exp_disabled" not in inner_proc_names
        assert "helper_disabled" not in inner_proc_names
        assert "nested_disabled" not in inner_proc_names

        # Check state inputs and multi-trigger filtering
        wait_state = proc.content.states[0]
        trigger_lists = [
            [t.lower() for t in inp.inputlist] for inp in wait_state.inputs
        ]
        assert ["sig_enabled"] in trigger_lists
        assert ["keep_sig"] in trigger_lists
        assert ["exp_enabled"] in trigger_lists
        assert ["timer_enabled"] in trigger_lists
        assert ["keep_timer"] in trigger_lists
        assert len(wait_state.inputs) == 5
        # Verify transitions count (1 start + 5 remaining inputs = 6)
        assert len(proc.transitions) == 6
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_select_if_codegen_ada_c_rust():
    for generator, files_to_check in (
        (AdaGenerator.generate, ("demo.ads", "demo.adb")),
        (CGenerator.generate, ("demo.h", "demo.c")),
        (RustGenerator.generate, ("demo.rs",)),
    ):
        ast, errors, warnings, tmpdir = _parse_model()
        cwd = os.getcwd()
        try:
            assert not errors, f"Unexpected parse errors: {errors}"
            os.chdir(tmpdir)
            proc = ast.processes[0]
            opts = types.SimpleNamespace(
                dumpAST=False, debug=False, shared=False, slim=False, stg=None
            )
            generator(proc, simu=False, options=opts)
            combined = ""
            for fname in files_to_check:
                with open(os.path.join(tmpdir, fname), "r", encoding="utf-8") as f:
                    combined += f.read()

            assert "sig_enabled" in combined
            assert "exp_enabled" in combined
            assert "helper_enabled" in combined
            assert "timer_enabled" in combined
            assert "sig_disabled" not in combined
            assert "sig_multi_disabled" not in combined
            assert "sig_both_off_1" not in combined
            assert "sig_both_off_2" not in combined
            assert "exp_disabled" not in combined
            assert "helper_disabled" not in combined
            assert "nested_disabled" not in combined
            assert "timer_disabled" not in combined
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmpdir, ignore_errors=True)


def test_select_if_rejects_non_ground_expression():
    pr_content = """\
    system bad;
        block bad;
            process bad;
                /* CIF TEXT (10, 10), (200, 100) */
                dcl flag Boolean := false;
                select if (flag);
                    timer t1;
                endselect;
                /* CIF ENDTEXT */
                START;
                    NEXTSTATE idle;
                state idle;
                endstate;
            endprocess bad;
        endblock;
    endsystem;
    """
    _, _, errors = ogParser.parse_pr(string=pr_content)
    assert errors, "Expected an error when using a DCL variable in select if"
    assert any("ground expression" in str(e) for e in errors)


def test_save_does_not_generate_signal_dummy():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from opengeode.opengeode import SDL_Scene
    from opengeode import Pr

    _ = QApplication.instance() or QApplication([])
    ast, errors, _, tmpdir = _parse_model()
    try:
        assert not errors
        block = ast.systems[0].blocks[0]
        scene = SDL_Scene(context="block")
        scene.ast = ast
        scene.render_everything(block)
        pr_lines = Pr.parse_scene(scene, full_model=True)
        pr_text = "\n".join(pr_lines)
        assert "dummy" not in pr_text.lower()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

