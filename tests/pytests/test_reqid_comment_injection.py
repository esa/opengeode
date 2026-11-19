#!/usr/bin/env python3
'''Security regression tests: requirement-ID comment injection (C, Ada, Rust).

The requirement IDs of a symbol come from the SDL annotation::

    /* CIF Keep Specific Geode _REQID_ '<id>' */

``<id>`` is a STRING token, and the grammar accepts ANY character except a
backslash and the closing quote between the quotes (sdl92.g, fragment STR -
the dot in ``~('\\\\' | '\\'')`` matches a newline). The parser strips only
the enclosing quotes (``.toString()[1:-1]``), so a model can carry a
multi-line requirement ID.

The three code generators joined the IDs into ONE comment line::

    // Requirement IDs: a, b

A line comment ends at the newline, so the continuation lines were emitted
as bare, live code. The payload below becomes a live ``#include`` plus a
``__attribute__((constructor))`` function, which runs when the generated
binary is loaded.

Every ID is now split on line breaks and each physical line gets its own
comment prefix (``//``, ``--  `` and ``//`` respectively); a lone carriage
return is neutralized as well (it is a line terminator for the Rust
reference and for some C/Ada toolchains), so no model text can ever leave a
comment.

Run with:
    cd tests/pytests && python3 -m pytest test_reqid_comment_injection.py -v
'''
import os

import pytest

from opengeode import AdaGenerator
from opengeode import CGenerator
from opengeode import RustGenerator
from opengeode import ogAST

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

# The payload from the security report (single-line comments, C flavour).
MALICIOUS_C = ('benign\n'
               '#include <stdlib.h>\n'
               'void __attribute__((constructor)) pwn() { system("id"); }\n'
               '//')
MALICIOUS_LF = 'benign\nevil_code_injected();//'
MALICIOUS_CR = 'benign\revil_code_injected();'
MALICIOUS_CRLF = 'benign\r\nevil_code_injected();'

BACKENDS = {
    'c': (CGenerator, '//'),
    'ada': (AdaGenerator, '--'),
    'rust': (RustGenerator, '//'),
}


def _symbol(req_ids, comment=None):
    '''A fresh AST symbol carrying the given requirement IDs'''
    task = ogAST.TaskAssign()
    task.elems = []
    task.req_ids = list(req_ids)
    task.comment = comment
    task.inputString = 'TASK z := c_true (19,21)'
    task.line = 19
    task.charPositionInLine = 20
    return task


# ------------------------------------------------------------ unit level

@pytest.mark.parametrize('backend', sorted(BACKENDS))
@pytest.mark.parametrize('payload', [
    MALICIOUS_C, MALICIOUS_LF, MALICIOUS_CR, MALICIOUS_CRLF,
    'simple-one-liner',
    'a\nb\nc',
    '',
])
def test_reqid_line_never_leaks_live_code(backend, payload):
    '''No emitted line may carry the payload outside a comment prefix.

    Every payload line ends with "//" so that, once outside a comment, it
    cannot swallow the closing characters the generator appends - which is
    precisely what makes it compile as live code in the generated file.
    '''
    module, _ = BACKENDS[backend]
    trace = module.traceability(_symbol([payload, 'REQ-2']))
    assert trace, 'no traceability lines generated'
    # The marker is reusable: it is never preceded by a comment prefix
    for line in trace:
        index = line.find('#include')
        while index != -1:
            assert line[:index].lstrip().startswith(_prefix(backend)), \
                f'live "#include" in {line!r}'
            index = line.find('#include', index + 1)
    for line in trace:
        index = line.find('pwn()')
        while index != -1:
            assert line[:index].lstrip().startswith(_prefix(backend)), \
                f'live "pwn()" in {line!r}'
            index = line.find('pwn()', index + 1)


def _prefix(backend, space=True):
    '''Comment marker that must open every generated line'''
    prefix = BACKENDS[backend][1]
    return prefix + ' ' if space else prefix


@pytest.mark.parametrize('backend', sorted(BACKENDS))
def test_reqid_splits_every_physical_line(backend):
    module, _ = BACKENDS[backend]
    trace = module.traceability(_symbol(['a\nb']))
    joined = '\n'.join(trace)
    # "Requirement IDs: a" then the second line on a comment line of its own
    assert any('Requirement IDs: a' in line for line in trace), joined
    assert any('b' == line.split(_prefix(backend))[1].strip()
               for line in trace), joined


@pytest.mark.parametrize('backend', sorted(BACKENDS))
def test_reqid_carriage_return_is_neutralized(backend):
    module, _ = BACKENDS[backend]
    trace = module.traceability(_symbol(['a\rb']))
    joined = '\n'.join(trace)
    assert '\r' not in joined, repr(joined)
    assert any('b' == line.split(_prefix(backend))[1].strip()
               for line in trace), joined


@pytest.mark.parametrize('backend', sorted(BACKENDS))
def test_reqid_single_line_is_unchanged(backend):
    '''Ordinary models keep the one-line "Requirement IDs:" comment'''
    module, _ = BACKENDS[backend]
    trace = module.traceability(_symbol(['REQ-1', 'REQ-2']))
    req_lines = [line for line in trace if 'Requirement IDs' in line]
    assert len(req_lines) == 1, trace
    assert 'REQ-1, REQ-2' in req_lines[0]
    assert '\n' not in req_lines[0]


@pytest.mark.parametrize('backend', sorted(BACKENDS))
def test_comment_field_is_neutralized_too(backend):
    '''The symbol comment follows the same code path'''
    module, _ = BACKENDS[backend]
    comment = ogAST.Comment()
    comment.text = MALICIOUS_LF
    comment.pos_x, comment.pos_y, comment.width, comment.height = 0, 0, 0, 0
    comment.inputString = 'COMMENT ' + MALICIOUS_LF
    trace = module.traceability(_symbol(['REQ-1'], comment=comment))
    for line in trace:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith(
            _prefix(backend)), repr(line)


# ------------------------------------------------------- generated source

@pytest.mark.parametrize('backend', sorted(BACKENDS))
def test_task_assign_emits_only_comments(backend):
    '''The task generator must not emit the payload as live code'''
    module, _ = BACKENDS[backend]
    code, _ = module._task_assign(_symbol([MALICIOUS_C]))
    for line in code:
        stripped = line.lstrip()
        assert stripped == '' or stripped.startswith(
            _prefix(backend)), repr(line)
        assert '#include' not in line or stripped.startswith(
            _prefix(backend)), repr(line)


# ------------------------------------------- the GUI re-saves these IDs

def test_pr_round_trip_keeps_payload_inside_the_cif():
    '''Pr.py writes each ID back as one _REQID_ CIF: still one string'''
    from opengeode import Pr  # pylint: disable=import-outside-toplevel

    symbol = _symbol([MALICIOUS_C])
    symbol.ast = symbol
    symbol.req_model = None
    lines = Pr.req_ids(symbol)
    assert lines, 'no _REQID_ line generated'
    for line in lines:
        assert line.startswith('/* CIF Keep Specific Geode _REQID_ ')
        assert line.endswith("' */")
        # The payload is inside the quoted STRING, not after the CIF
        assert line.count('*/') == 1


# ------------------------------------- the model is written back as .pr too

@pytest.mark.parametrize('payload', [
    '*/ task evil := 1; /*',          # closes the CIF, then live .pr text
    'a\n*/task evil := 1; //',        # same, through a line break
    "it's",                           # a quote: ends the SDL string
    'a\\b',                           # a backslash: escapes the next char
    'REQ-1',                          # ordinary ID: untouched
])
def test_pr_reqid_cannot_escape_its_cif_comment(payload):
    '''The ID is re-written into the .pr inside a CIF comment.

    A "*/" in the value used to close the CIF early, so the remainder was
    written back as live model text when the model was saved again.
    '''
    from opengeode import Pr  # pylint: disable=import-outside-toplevel

    symbol = _symbol([payload])
    symbol.ast = symbol
    symbol.req_model = None
    for line in Pr.req_ids(symbol):
        assert line.startswith('/* CIF Keep Specific Geode _REQID_ ')
        assert line.endswith("' */")
        body = line[len('/* CIF Keep Specific Geode _REQID_ '):-4]
        # body is "'<value>" - strip the opening quote the CIF adds
        assert body.startswith("'"), repr(line)
        body = body[1:]
        # The only comment terminator is the one closing the CIF
        assert body.count('*/') == 0, repr(line)
        # No unescaped quote may end the SDL string early
        index = 0
        while index < len(body):
            if body[index] == '\\':
                index += 2
                continue
            assert body[index] != "'", repr(line)
            index += 1


def test_pr_reqid_ordinary_id_is_unchanged():
    '''Ordinary IDs must round-trip byte for byte'''
    from opengeode import Pr  # pylint: disable=import-outside-toplevel

    symbol = _symbol(['REQ-1', 'OPENGEODE_TEST_REQID_01'])
    symbol.ast = symbol
    symbol.req_model = None
    assert Pr.req_ids(symbol) == [
        "/* CIF Keep Specific Geode _REQID_ 'REQ-1' */",
        "/* CIF Keep Specific Geode _REQID_ 'OPENGEODE_TEST_REQID_01' */",
    ]

