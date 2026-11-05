#!/usr/bin/env python3
'''Security regression tests: string-literal injection in the C backend.

The SDL/ASN.1 parser keeps the source escapes of a quoted string verbatim in
``PrimStringLiteral.value`` (sdl92.g: ESC1 = \\' | \\\\, ESC2 = \\" | \\\\). An
IA5String literal such as::

    task s := "benign\\";evil();//";

therefore reaches the C generator with a literal backslash before the quote.
The old code did ``value[1:-1].replace('"', '\\\\"')``, which turned that
backslash-quote into a backslash-backslash-quote: the C string literal closed
early and the rest of the model text was compiled as live C code (silently,
with no compiler warning).

The fix interprets the SDL escapes first and then re-escapes for C (the same
two-step approach the Ada backend uses), so every model string always stays
inside one C string literal.

Run with:
    cd tests/pytests && python3 -m pytest test_c_string_injection.py -v
'''
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

from opengeode import CGenerator
from opengeode import ogAST
from opengeode.ogParser import parse_pr

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(TESTS_DIR))
STRINGS_MODEL = os.path.join(REPO_ROOT, 'tests', 'testsuite', 'test-strings')

# The payload from the security report: a quote that closes the C literal,
# then C statements, then a comment that swallows the trailing quote.
INJECTION = '");extern int system(const char*);system((char[]){\'i\',\'d\',0});//'


class _Options:
    '''The subset of the CLI options the C backend reads.'''
    dumpAST = False


# --------------------------------------------------------------- unit level

@pytest.mark.parametrize('raw, expected', [
    ('benign\\";evil();//', 'benign";evil();//'),      # SDL \" -> a quote
    ('say \\"hi\\"', 'say "hi"'),
    ("it\\'s", "it's"),                                # SDL \' -> a quote
    ('a\\\\b', 'a\\b'),                                # SDL \\ -> one backslash
    ('plain', 'plain'),
    ('h\u00e9h\u00e9', 'h\u00e9h\u00e9'),              # non-ASCII survives
    ('back\\slash', 'back\\slash'),                    # other escapes are literal
])
def test_sdl_string_unescape(raw, expected):
    assert CGenerator.sdl_string_unescape(raw) == expected


@pytest.mark.parametrize('text', [
    INJECTION,
    'a"b',
    'a\\b',
    'line1\nline2',
    'tab\there',
    'carriage\rreturn',
])
def test_c_string_literal_always_closes_once(text):
    '''The escaped body must not contain an unescaped quote or backslash.'''
    escaped = CGenerator.c_escape_string(text)
    index = 0
    while index < len(escaped):
        if escaped[index] == '\\':
            index += 2          # an escape consumes the next character
            continue
        assert escaped[index] != '"', repr(escaped)
        index += 1


@pytest.mark.parametrize('raw', [
    'benign\\";evil();//',
    'a\\\\"b',
    'x\\"y\\"z',
])
def test_c_string_literal_round_trip(raw):
    '''The literal must denote exactly the text the model wrote.'''
    literal = CGenerator.c_string_literal(raw)
    assert literal.startswith('"') and literal.endswith('"')
    body = literal[1:-1]
    # Un-escape the C literal the way a C compiler would
    out, index = [], 0
    while index < len(body):
        if body[index] == '\\':
            mapping = {'n': '\n', 'r': '\r', 't': '\t', '"': '"', '\\': '\\'}
            out.append(mapping[body[index + 1]])
            index += 2
            continue
        out.append(body[index])
        index += 1
    assert ''.join(out) == CGenerator.sdl_string_unescape(raw)


# ------------------------------------------------------------ end to end

def _generate_c_with_injected_string():
    '''Run the C generator on the test-strings model with a malicious IA5String'''
    workdir = tempfile.mkdtemp(prefix='c-injection-')
    for name in ('og.pr', 'dataview-uniq.asn'):
        shutil.copy(os.path.join(STRINGS_MODEL, name), workdir)

    model = os.path.join(workdir, 'og.pr')
    with open(model, encoding='utf-8') as model_file:
        content = model_file.read()
    benign = "task result := result // 'Hello!';"
    assert benign in content
    payload = 'task ia5 := "benign\\";extern int system(const char*);' \
              "system((char[]){'i','d',0});//\";"
    with open(model, 'w', encoding='utf-8') as model_file:
        model_file.write(content.replace(benign, payload, 1))

    cwd = os.getcwd()
    os.chdir(workdir)
    try:
        ast, errors, _ = parse_pr(files=[model])
        assert not errors, errors
        CGenerator.generate(ast.processes[0], options=_Options())
        with open(os.path.join(workdir, 'og.c'), encoding='utf-8') as gen:
            return gen.read(), workdir
    finally:
        os.chdir(cwd)


def test_ia5string_assignment_does_not_inject_c_code():
    '''The reported vector: a TASK assigning an IA5String literal.'''
    generated, _ = _generate_c_with_injected_string()

    # The whole payload must be inside one string literal: the quote that
    # follows "benign" is escaped, so `system(` is never live code.
    assert 'extern int system(const char*);' in generated
    for line in generated.split('\n'):
        if 'extern int system' in line and '//' not in line.split('extern')[0]:
            stripped = line.strip()
            # It must be part of a string literal, i.e. contain the escaped quote
            assert 'benign\\"' in stripped, repr(line)


def test_ia5string_assignment_compiles_and_is_inert(tmp_path):
    '''Compile the generated C (if a toolchain is available) and run it.

    Before the fix the injected `system(...)` ran and printed the user id.
    After the fix the payload is printed as ordinary text.
    '''
    if not shutil.which('gcc') or not shutil.which('asn1scc'):
        pytest.skip('gcc/asn1scc not available')

    workdir = tmp_path / 'model'
    workdir.mkdir()
    for name in ('og.pr', 'dataview-uniq.asn'):
        shutil.copy(os.path.join(STRINGS_MODEL, name), workdir / name)
    content = (workdir / 'og.pr').read_text(encoding='utf-8')
    benign = "task result := result // 'Hello!';"
    payload = 'task ia5 := "benign\\";extern int system(const char*);' \
              "system((char[]){'i','d',0});//\";"
    (workdir / 'og.pr').write_text(content.replace(benign, payload, 1),
                                   encoding='utf-8')

    # Generate in a clean interpreter: the generator mutates the AST, and the
    # parser keeps module-level type tables, so a fresh process is the only
    # way to guarantee this test is independent of whatever ran before.
    generator = textwrap.dedent('''
        import sys
        from opengeode import CGenerator
        from opengeode.ogParser import parse_pr

        class Options:
            dumpAST = False

        ast, errors, _ = parse_pr(files=['og.pr'])
        assert not errors, errors
        CGenerator.generate(ast.processes[0], options=Options())
    ''')
    gen = subprocess.run([sys.executable, '-c', generator], cwd=workdir,
                         capture_output=True, text=True, timeout=300)
    assert gen.returncode == 0, gen.stdout + gen.stderr
    assert (workdir / 'og_datamodel.asn').exists()

    asn = subprocess.run(
        ['asn1scc', '-c', '-ig', '-typePrefix', 'asn1Scc', '-renamePolicy', '3',
         '-equal', '-fp', 'AUTO', 'dataview-uniq.asn', 'og_datamodel.asn'],
        cwd=workdir, capture_output=True, text=True)
    assert asn.returncode == 0, asn.stdout + asn.stderr
    shutil.copy(os.path.join(STRINGS_MODEL, 'test_c.c'), workdir / 'test_c.c')

    build = subprocess.run(
        ['gcc', '-Wall', '-O0', 'test_c.c', 'og.c', 'dataview-uniq.c',
         'og_datamodel.c', 'asn1crt.c', '-o', 'test_c'],
        cwd=workdir, capture_output=True, text=True)
    assert build.returncode == 0, build.stderr

    run = subprocess.run([str(workdir / 'test_c')], cwd=workdir,
                         capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    # The payload is inert: it is never executed.
    assert 'uid=' not in run.stdout
    generated = (workdir / 'og.c').read_text(encoding='utf-8')
    assert 'extern int system' in generated


# ------------------------------------------------- second vector: writeln

def test_writeln_hex_literal_does_not_inject_c_code():
    '''A hex literal decodes to arbitrary bytes, including a quote.

    `write`/`writeln` used to paste ``param.printable_string`` straight into
    ``printf("...")``, so a hex literal spelling out a quote closed the format
    string and the remaining bytes became live C code.
    '''
    workdir = tempfile.mkdtemp(prefix='c-injection-hex-')
    for name in ('og.pr', 'dataview-uniq.asn'):
        shutil.copy(os.path.join(STRINGS_MODEL, name), workdir)
    model = os.path.join(workdir, 'og.pr')
    with open(model, encoding='utf-8') as model_file:
        content = model_file.read()
    benign = "task result := result // 'Hello!';"
    hex_payload = INJECTION.encode().hex()
    assert benign in content
    with open(model, 'w', encoding='utf-8') as model_file:
        model_file.write(content.replace(benign, f"call writeln('{hex_payload}'H);", 1))

    cwd = os.getcwd()
    os.chdir(workdir)
    try:
        ast, errors, _ = parse_pr(files=[model])
        assert not errors, errors
        CGenerator.generate(ast.processes[0], options=_Options())
        with open(os.path.join(workdir, 'og.c'), encoding='utf-8') as gen:
            generated = gen.read()
    finally:
        os.chdir(cwd)

    # No printf may be broken by the decoded quote: the format string is
    # escaped, so the payload appears as \\" inside it.
    for line in generated.split('\n'):
        if 'extern int system' in line and line.strip().startswith('printf('):
            assert '\\"' in line, repr(line)
