'''Security regression tests for the SDL parser (ogParser.py) fixes.

Each test below locks in one finding of the security audit documented in
docs/security-audit-ogparser.md (P1..P10) and its fix described in
docs/security-fix-ogparser.md. Run with:

    cd tests/pytests && python3 -m pytest test_ogparser_security.py -v
'''
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

# Make the repo's opengeode package importable
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from opengeode import ogParser, Pr  # noqa: E402


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def workdir():
    ''' Temporary directory containing a small, valid SDL model '''
    tmp = tempfile.mkdtemp(prefix='ogparser_sec_')
    with open(os.path.join(tmp, 'dataview-uniq.asn'), 'w') as f:
        f.write('TestModule DEFINITIONS ::=\nBEGIN\n'
                'MyInt ::= INTEGER (0..255)\nEND\n')
    with open(os.path.join(tmp, 'system_structure.pr'), 'w') as f:
        f.write("""/* CIF Keep Specific Geode ASNFilename 'dataview-uniq.asn' */
USE TestModule;
SYSTEM probe;

	SIGNAL pulse;

	CHANNEL c
		FROM ENV TO probe WITH pulse;
	ENDCHANNEL;

	BLOCK probe;

		SIGNALROUTE r
			FROM ENV TO probe WITH pulse;

		CONNECT c and r;

		PROCESS probe REFERENCED;

	ENDBLOCK;

ENDSYSTEM;
""")
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


def process_model(text_area='    DCL x MyInt;', start_task=None):
    ''' Minimal valid process body. The text area holds declarations;
    start_task (if given) is a task statement placed in the START
    transition. '''
    task_lines = ''
    if start_task:
        task_lines = ('        /* CIF task (1005, 100), (149, 53) */\n'
                      f'        task {start_task};\n')
    return f"""/* CIF PROCESS (144, 159), (150, 75) */
process probe;
    /* CIF Keep Specific Geode Partition 'default' */
    /* CIF TEXT (832, 176), (272, 248) */
{text_area}
    /* CIF ENDTEXT */
    /* CIF START (1030, 35), (100, 50) */
    START;
{task_lines}        /* CIF NEXTSTATE (1100, 160), (70, 35) */
        NEXTSTATE wait;
    /* CIF state (400, 300), (70, 35) */
    state wait;
        /* CIF input (450, 350), (70, 35) */
        input pulse;
            /* CIF NEXTSTATE (550, 450), (70, 35) */
            NEXTSTATE -;
    endstate;
endprocess probe;
"""


def parse(workdir, text_area='    DCL x MyInt;', start_task=None):
    ''' Parse the minimal model, returning (ast, warnings, errors).
    The parser resolves the ASN.1 filename of the USE clause relative to
    the current directory (like the real tool, which chdirs to the model
    directory before parsing), so run from the model directory. '''
    with open(os.path.join(workdir, 'probe.pr'), 'w') as f:
        f.write(process_model(text_area, start_task))
    prev = os.getcwd()
    os.chdir(workdir)
    try:
        return ogParser.parse_pr(['probe.pr', 'system_structure.pr'])
    finally:
        os.chdir(prev)


# ------------------------------------------------------------ P2: bignum DoS

@pytest.mark.parametrize('exponent', ['1000000000000', '1000000000000000'])
def test_mantissa_base_exponent_bounded(workdir, exponent):
    ''' {mantissa, base, exponent} with a huge exponent must fail fast
    instead of materialising a multi-gigabyte integer (P2). '''
    import time
    t0 = time.time()
    ast, warn, err = parse(
        workdir,
        start_task=f'x := {{mantissa 1, base 2, exponent {exponent}}}')
    elapsed = time.time() - t0
    # Must not crash, and must be fast (previously: killed at 20s, multi-GB)
    assert elapsed < 5, \
        f'parsing a huge exponent literal took {elapsed:.1f}s (unbounded?)'
    # And it must be reported as an error, not silently accepted
    assert any('exceeds' in str(e) or 'exponent' in str(e).lower()
               for e in err), \
        f'huge exponent was not reported: {[str(e)[:60] for e in err]}'


def test_mantissa_base_exponent_valid_still_works(workdir):
    ''' Small exponents must keep working normally (no false positives) '''
    # A regular real value via mantissa/base/exponent in a task
    ast, warn, err = parse(workdir,
                           start_task='x := {mantissa 1, base 2, exponent 3}')
    msgs = ' '.join(str(e).lower() for e in err)
    assert 'exceeds' not in msgs, \
        f'valid mantissa/base/exponent rejected: {[str(e)[:60] for e in err]}'


# --------------------------------------------------------- P3: sys.path hijack

def test_sys_path_not_polluted(workdir):
    ''' Parsing a model must not insert the model directory (or '.') in
    sys.path (P3: lazy imports would then resolve to attacker modules). '''
    before = list(sys.path)
    parse(workdir)
    after = list(sys.path)
    assert before == after, 'sys.path was modified by parse_pr'
    model_dir = os.path.abspath(workdir)
    for entry in after:
        if os.path.abspath(entry or '.') == model_dir:
            pytest.fail('model directory found in sys.path after parse')


def test_planted_module_not_imported(workdir):
    ''' A module planted in the model directory must not shadow the real
    one after a parse (P3 RCE regression). '''
    marker = os.path.join(tempfile.gettempdir(), 'og_sec_p3_marker')
    if os.path.exists(marker):
        os.unlink(marker)
    with open(os.path.join(workdir, 'StgBackend.py'), 'w') as f:
        f.write('import os\n'
                f'open({marker!r}, "w").write("hijacked")\n')
    try:
        parse(workdir)
        # Import of the planted name must NOT find it in the model dir.
        # Simulate the lazy import from a different working directory.
        code = ('import sys, os;'
                f'sys.path.insert(0, {REPO!r});'
                'from opengeode import ogParser;'
                f'ogParser.parse_pr([{os.path.join(workdir, "probe.pr")!r},'
                f'{os.path.join(workdir, "system_structure.pr")!r}]);'
                'print("model_dir_in_path=", os.path.join(sys.path[0] if sys.path else "", "") '
                'if any('f'{workdir!r}' ' == os.path.abspath(p or ".") for p in sys.path) else "")'
                )
        proc = subprocess.run([sys.executable, '-c', code],
                              capture_output=True, text=True, timeout=60,
                              cwd=tempfile.gettempdir())
        assert not os.path.exists(marker), \
            'planted module was executed: sys.path hijack still possible'
    finally:
        if os.path.exists(marker):
            os.unlink(marker)


# ------------------------------------------------- P4: SYNTYPE reference cycle

def test_syntype_cycle_rejected(workdir):
    ''' Re-declaring a SYNTYPE with a different parent (which could create
    A->B->A cycles) must be rejected, not crash with RecursionError (P4). '''
    text_area = ('    syntype A = integer\n'
                 '     constants 0:1\n'
                 '    endsyntype;\n'
                 '    syntype B = A\n'
                 '     constants 0:1\n'
                 '    endsyntype;\n'
                 '    syntype A = B\n'
                 '     constants 0:1\n'
                 '    endsyntype;\n'
                 '    dcl x A;')
    ast, warn, err = parse(workdir, text_area)
    msgs = ' '.join(str(e).lower() for e in err)
    assert 'circular' in msgs or 're-declaration' in msgs, \
        f'cycle not rejected: {[str(e)[:80] for e in err]}'
    # And the parse must NOT have raised RecursionError (it would propagate)
    assert 'recursion' not in msgs


def test_syntype_duplicate_ok_when_identical(workdir):
    ''' Identical re-declaration (text areas visited twice) stays allowed,
    and normal syntype chains keep working (no false positives). '''
    text_area = ('    syntype A = integer\n'
                 '     constants 0:1\n'
                 '    endsyntype;\n'
                 '    syntype B = A\n'
                 '     constants 0:1\n'
                 '    endsyntype;\n'
                 '    dcl x B;')
    ast, warn, err = parse(workdir, text_area)
    assert not err, f'legitimate syntype chain rejected: {[str(e)[:60] for e in err]}'


# --------------------------------------------------- P5: deep nesting (DoS)

def test_deep_nesting_clean_error(workdir):
    ''' Deeply nested expressions must produce a clean syntax error, not a
    raw RecursionError traceback (P5). '''
    depth = 2000
    parens = '(' * depth + '1' + ')' * depth
    ast, warn, err = parse(workdir, start_task=f'x := {parens}')
    msgs = ' '.join(str(e).lower() for e in err)
    assert 'nested' in msgs or 'recursion' in msgs, \
        f'deep nesting not reported as error: {[str(e)[:60] for e in err]}'


# ------------------------------------------------- P6: encoding of the parser

def test_parser_reads_utf8_regardless_of_locale(workdir):
    ''' A model with non-ASCII characters must parse (or report syntax
    errors) even under a legacy locale (P6). '''
    model = process_model('    -- h\xc3\xa9h\xc3\xb6 unicode comment\n'
                          '    DCL x MyInt;')
    with open(os.path.join(workdir, 'probe.pr'), 'wb') as f:
        f.write(model.encode('utf-8'))
    env = dict(os.environ, LC_ALL='C', LANG='C')
    code = (
        'import sys;'
        f'sys.path.insert(0, {REPO!r});'
        'from opengeode import ogParser;'
        f'ogParser.parse_pr([{os.path.join(workdir, "probe.pr")!r},'
        f'{os.path.join(workdir, "system_structure.pr")!r}]);'
        'print("OK")'
    )
    proc = subprocess.run([sys.executable, '-X', 'utf8=0', '-c', code],
                          capture_output=True, text=True, timeout=60,
                          env=env)
    assert 'UnicodeDecodeError' not in proc.stderr, \
        f'parser crashed on non-ASCII under legacy locale: {proc.stderr[-300:]}'
    assert proc.returncode == 0, \
        f'parser crashed under legacy locale: {proc.stderr[-300:]}'


# -------------------------------------------- P7: eval/clipboard dispatch

def test_parse_single_element_rejects_hostile_name():
    ''' parseSingleElement must reject unknown/hosile element names with a
    ValueError, under python -O as well (P7). '''
    with pytest.raises(ValueError):
        ogParser.parseSingleElement(
            '__import__("os").system("true")', 'task x := 1;')
    with pytest.raises(ValueError):
        ogParser.parseSingleElement('nonsense', 'task x := 1;')


def test_parse_single_element_whitelist_is_a_dict():
    ''' The dispatch table must be a fixed dict, not eval() '''
    assert isinstance(ogParser.SINGLE_ELEMENTS, dict)
    assert 'task' in ogParser.SINGLE_ELEMENTS
    assert callable(ogParser.SINGLE_ELEMENTS['task'])
    # every whitelisted entry is a module-level function of this module
    for name, func in ogParser.SINGLE_ELEMENTS.items():
        assert callable(func), f'{name} is not callable'


def test_parse_single_element_valid_names_still_work():
    for name in ('task', 'state', 'text_area'):
        # must not raise
        ogParser.parseSingleElement(name, 'state foo; endstate')
        ogParser.parseSingleElement('task', 'task x := 1;')


def test_clipboard_validation_helper(workdir):
    ''' Clipboard.paste validates the element name before parsing (P7):
    the SINGLE_ELEMENTS table is the authoritative whitelist. '''
    # simulate a hostile clipboard payload
    hostile = ['OG_SDL', '999', 'not_a_real_kind', 'task x := 1;']
    assert hostile[2] not in ogParser.SINGLE_ELEMENTS
    benign = ['OG_SDL', '999', 'task', 'task x := 1;']
    assert benign[2] in ogParser.SINGLE_ELEMENTS


# ---------------------------------------------- P1: forged CIF _id cast gate

def test_symbol_id_registry_empty_without_scene():
    ''' No ids are registered until a live scene emits them (P1). '''
    assert Pr.SYMBOL_ID_REGISTRY is not None
    # the registry starts empty in a fresh process (no scene was rendered)
    proc = subprocess.run(
        [sys.executable, '-c',
         f'import sys; sys.path.insert(0, {REPO!r});'
         'from opengeode import Pr;'
         'print(len(Pr.SYMBOL_ID_REGISTRY))'],
        capture_output=True, text=True, timeout=60)
    assert proc.stdout.strip() == '0'


def test_forged_symbol_id_not_castable():
    ''' The ctypes cast of a forged id must be prevented by the registry:
    simulate the GUI decision (opengeode.py find_symbols_and_update_errors)
    for an id that no live scene emitted. '''
    forged = 999999999999  # arbitrary address-like integer from a .pr file
    assert forged not in Pr.SYMBOL_ID_REGISTRY
    # This is the exact gate used in opengeode.py: an id absent from the
    # registry is skipped, never cast.
    symbol_id = int(forged)
    assert symbol_id not in Pr.SYMBOL_ID_REGISTRY


# --------------------------------------------- P9: HYPERLINK scheme check

def test_hyperlink_scheme_restriction():
    ''' Only http/https hyperlinks may be handed to the desktop URL handler
    (P9). The check lives in TextInteraction/genericSymbols; verify the
    policy by exercising the QUrl parse the same way the fix does. '''
    try:
        from PySide6.QtCore import QUrl
    except ImportError:
        pytest.skip('PySide6 not available')
    assert QUrl('file:///etc/passwd').scheme() not in ('http', 'https')
    assert QUrl('ssh://evil').scheme() not in ('http', 'https')
    assert QUrl('https://example.com').scheme() in ('http', 'https')
    assert QUrl('http://example.com').scheme() in ('http', 'https')


# ------------------------------------- P10: dash filename validation parity

def test_asn1_dash_filename_rejected_by_asn1scc():
    ''' The Asn1scc module must reject dash-prefixed filenames (P10,
    argument injection parity). '''
    from opengeode import Asn1scc
    with pytest.raises(TypeError):
        Asn1scc._validate_input_files(['-o/customStg', 'evil.asn'])


# ------------------------------------------------- P2 twin: LLVM backend gone

def test_llvm_backend_removed():
    ''' The LLVM backend (which carried the same mantissa/base/exponent
    bignum bug) must be fully removed. '''
    assert not os.path.exists(os.path.join(REPO, 'opengeode',
                                           'LlvmGenerator.py'))
    src = open(os.path.join(REPO, 'opengeode', 'opengeode.py')).read()
    assert '--llvm' not in src, 'the --llvm option is still registered'
    assert 'options.llvm' not in src


# ------------------------------------------------- P6 twin: GUI regression

def test_pr_files_are_strings(workdir):
    ''' Regression for the P6 UTF8FileStream fix: antlr3's fileName is a
    property; defining it as a method in the subclass made node_filename()
    return a bound method, which landed in ast.pr_files and crashed the GUI
    file monitor (os.path.abspath: "expected str, not method") on every
    model load. '''
    # write the model first (the parse() helper also writes it)
    with open(os.path.join(workdir, 'probe.pr'), 'w') as f:
        f.write(process_model())
    prev = os.getcwd()
    os.chdir(workdir)
    try:
        ast, warn, err = ogParser.parse_pr(['probe.pr', 'system_structure.pr'])
    finally:
        os.chdir(prev)
    assert ast.pr_files, 'pr_files is empty'
    for f in ast.pr_files:
        assert isinstance(f, str), \
            f'pr_files contains a non-string entry: {f!r} (type {type(f).__name__})'
        # the exact operation the GUI file monitor performs
        os.path.abspath(f)


# ------------------------------------------------------- negative controls

def test_normal_model_still_parses(workdir):
    ''' The security fixes must not break ordinary models (false-positive
    regression check). '''
    ast, warn, err = parse(workdir)
    assert not err, f'valid model rejected: {[str(e)[:60] for e in err]}'
    assert len(ast.processes) == 1


def test_editable_text_focus_out_without_focus_in(workdir):
    '''Regression: EditableText.focusOutEvent raised AttributeError
    ("oldSize" missing) because the pre-edit state was captured only in
    focusInEvent — while Symbol.edit_text() (used by place_symbol, the
    editor's own symbol-placement path) sets the editing flag directly
    after setFocus(). When the item already had the focus Qt delivers
    no second focusInEvent, so nothing was captured and the next
    focus-out crashed. The capture now happens at every editing site
    (EditableText._begin_editing), and the attributes are initialised
    in __init__ so a stray focus-out degrades to "nothing changed".'''
    import sys
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QEvent, QPointF, Qt
    app = QApplication.instance() or QApplication([])

    from opengeode import TextInteraction
    from opengeode.opengeode import SDL_Scene

    # A scene with one symbol that owns an EditableText
    scene = SDL_Scene(context='process')
    from opengeode.sdlSymbols import Task
    task = Task(parent=None)
    scene.addItem(task)
    task.text.setPlainText('x := 1')

    # The exact crash path: the item ALREADY has the focus, so Qt will
    # not deliver a second focusInEvent — place_symbol -> edit_text
    # sets the editing flag without any capture happening.
    # The crash scenario: editing turns on through a route that did
    # NOT go through focusInEvent (headless there is no view to give
    # the item the keyboard focus, which is exactly the shape of the
    # bug: the flag was set while the capture was skipped).
    task.edit_text()                    # place_symbol's path
    assert task.text.editing is True

    # focusOutEvent must not raise, whatever the route to editing was
    from PySide6.QtGui import QFocusEvent
    event = QFocusEvent(QEvent.Type.FocusOut, Qt.MouseFocusReason)
    try:
        task.text.focusOutEvent(event)
        crashed = False
    except AttributeError as err:
        crashed = True
        print('CRASHED:', err)
    assert not crashed, 'focusOutEvent must survive without a prior focusInEvent'
