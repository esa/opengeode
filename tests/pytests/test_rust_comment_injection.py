#!/usr/bin/env python3
'''Security regression tests: comment injection in the Rust backend.

Model-supplied text (informal tasks, requirement IDs, informal decision
texts, trace strings) may contain embedded line breaks. Rust line comments
end at the newline, so a naive one-line ``//`` prefix lets the model inject
live code into the generated file — the Ada and C backends neutralize this
(``text.replace('\\n', '\\n-- ')`` / ``text.replace('\\n', '\\n// ')``) and
the Rust backend must do the same, for every physical line.

A carriage return is neutralized as well: the Rust reference permits a
bare CR as a line terminator (unlike Ada/C, where CR is not special in a
line comment), so ``// innocent\\rmalicious()`` could end the comment early
on a conforming host and leak the tail as live code.

Run with:
    cd tests/pytests && python3 -m pytest test_rust_comment_injection.py -v
'''
import os
import subprocess
import sys
import tempfile

import pytest

from opengeode.ogParser import parse_pr, parseSingleElement
from opengeode import RustGenerator
from opengeode import ogAST

COMMENT = RustGenerator._comment
TASK_INFORMAL = RustGenerator._task_informal_text
TRACEABILITY = RustGenerator.traceability

MALICIOUS_LF = 'innocent\nevil_code_injected();'
MALICIOUS_CR = 'innocent\revil_code_injected();'
MALICIOUS_CRLF = 'innocent\r\nevil_code_injected();'

# Minimal process with an ASN.1 dataview (same shape as test_codegen1.py)
COMMON = '''
   system parse;
        /* CIF TEXT (123, 141), (210, 140) */
        use dataview comment 'data/dv.asn';
        /* CIF ENDTEXT */
        block parse;
        process parse;
            start;
                nextstate wait;
            state wait;
            endstate;
        endprocess parse;
        endblock;
   endsystem;
'''


def _parse_process():
    '''Minimal process AST for on-the-fly element parsing'''
    # parse_pr resolves the ASN.1 comment relative to the CWD: run from
    # this directory (tests/pytests) where data/dv.asn lives.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ast, errs, warns = parse_pr(string=COMMON)
    return ast.processes[0]


def _parse_informal_task(text):
    '''Parse a TASK containing arbitrary (possibly malicious) informal text'''
    proc = _parse_process()
    # Informal text: single quotes, free text, may span lines (STR token
    # in the grammar matches any character including \\n and \\r).
    task_ast, err, warn, _, _ = parseSingleElement(
        'task', f"task '{text}';", proc)
    return task_ast


# ------------------------------------------------------------ _comment unit

@pytest.mark.parametrize('payload', [
    MALICIOUS_LF, MALICIOUS_CR, MALICIOUS_CRLF,
    'simple one-liner',
    'line1\nline2\nline3',
    'trailing newline\n',
    '',
])
def test_comment_never_leaks_live_code(payload):
    '''Every emitted line must be a full-line // comment, or empty'''
    for line in COMMENT(payload):
        assert line == '' or line.startswith('// '), repr(line)
        # No line may carry the payload outside a comment prefix
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith('//'), repr(line)


def test_comment_splits_every_physical_line():
    assert COMMENT('a\nb') == ['// a', '// b']
    assert COMMENT('a\rb') == ['// a', '// b']
    assert COMMENT('a\r\nb') == ['// a', '// b']


def test_comment_empty_line_gets_bare_prefix():
    # Empty continuation lines keep the prefix (Ada/C convention) so
    # nothing is ever emitted as bare code
    assert COMMENT('a\n\nb') == ['// a', '// ', '// b']


# ------------------------------------------------- informal task end to end

@pytest.mark.parametrize('payload', [MALICIOUS_LF, MALICIOUS_CR])
def test_informal_task_comment_injection(payload):
    '''A multiline informal TASK must become one comment per line'''
    task_ast = _parse_informal_task(payload)
    # Sanity: the parser kept the embedded line break in the text
    elems = getattr(task_ast, 'elems', [])
    joined = ''.join(str(e) for e in elems)
    assert 'innocent' in joined, f'payload lost in parse: {elems!r}'
    code, _ = TASK_INFORMAL(task_ast)
    assert code, 'no code generated for informal task'
    for line in code:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith('//'), repr(line)
    # The payload must never appear as live (non-comment) code
    for line in code:
        assert 'evil_code_injected' not in line or \
            line.lstrip().startswith('//'), repr(line)


def test_informal_task_multiline_comment_content():
    task_ast = _parse_informal_task('hello\nworld')
    code, _ = TASK_INFORMAL(task_ast)
    assert '// hello' in code
    assert '// world' in code


# ----------------------------------------------------- traceability / req_ids

def test_traceability_neutralizes_newline_in_req_ids():
    '''req_ids come from STRING tokens that may span lines'''
    sym = _parse_informal_task('x')
    sym.req_ids = ['R1\nfn injected() {}', 'R2']
    trace = TRACEABILITY(sym)
    for line in trace:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith('//'), repr(line)
        assert 'injected' not in line or line.lstrip().startswith('//')


def test_traceability_neutralizes_newline_in_trace():
    sym = _parse_informal_task('line1\nline2')
    trace = TRACEABILITY(sym)
    for line in trace:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith('//'), repr(line)
    # the multiline payload must land as one comment PER LINE: the trace
    # string contains "TASK 'line1\nline2' (...)", so the second source
    # line opens its own comment line.
    flat = '\n'.join(trace)
    assert flat.count('\n') >= 1
    assert any(line.startswith('// ') and 'line1' in line for line in trace)
    assert any(line.startswith('// ') and 'line2' in line for line in trace)
    # and no line ever carries payload outside a comment
    for line in trace:
        assert line == '' or line.lstrip().startswith('//'), repr(line)


# --------------------------------------------------------- informal decision

def _parse_informal_decision(text):
    proc = _parse_process()
    dec_ast, err, warn, _, _ = parseSingleElement(
        'decision', f"decision '{text}'; enddecision;", proc)
    return dec_ast


def test_informal_decision_comment_injection():
    '''Informal decision text is free text and may span lines'''
    dec_ast = _parse_informal_decision('safe text\nevil_decision_code();')
    assert isinstance(dec_ast, ogAST.Decision)
    assert dec_ast.kind == 'informal_text'
    code, _ = RustGenerator.generate(dec_ast)
    for line in code:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith('//'), repr(line)
        assert 'evil_decision_code' not in line or \
            line.lstrip().startswith('//')


# --------------------------------------------------------- rustc compile proof

def test_emitted_comments_are_inert_rust():
    '''The emitted comment lines must not alter code when compiled'''
    payload = 'innocent\n@@@ not valid rust if it leaks @@@\r' \
              'fn injected() { @@@ }'
    lines = COMMENT(payload)
    src = '\n'.join(lines) + '\nfn main() { let _ = 1; }\n'
    with tempfile.TemporaryDirectory() as tmp:
        src_file = os.path.join(tmp, 'probe.rs')
        with open(src_file, 'w') as f:
            f.write(src)
        try:
            res = subprocess.run(
                ['rustc', '--edition', '2021', '--emit=metadata',
                 src_file, '-o', os.path.join(tmp, 'probe.rmeta')],
                capture_output=True, text=True, timeout=120)
        except FileNotFoundError:
            pytest.skip('rustc not available')
        assert res.returncode == 0, res.stderr
        assert 'injected' not in res.stderr and \
            'error' not in res.stderr, res.stderr
