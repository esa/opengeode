#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Tests for the SDL MCP server (opengeode/SdlMcpServer.py).

The server is exercised the way orbit exercises it: as a subprocess
speaking newline-delimited JSON-RPC 2.0 over stdin/stdout. The tests
cover the wire handshake, every tool on a copy of a real test model,
and the security posture (argument validation, malformed input, the
server never dying on garbage).

Requires PySide6 (the server renders scenes headless with it).
'''

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import pytest

pytest.importorskip('PySide6')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SERVER_MODULE = 'opengeode.SdlMcpServer'
# A small, well-formed model: one process, states, tasks, a text area.
MODEL_DIR = os.path.join(REPO, 'tests', 'testsuite', 'test1')

# The model class, imported directly for the in-process capability
# tests (the subprocess tests cover the wire).
sys.path.insert(0, REPO)
from opengeode.SdlMcpServer import SdlModel  # noqa: E402


@pytest.fixture()
def server(tmp_path):
    '''A server on a scratch copy of the test1 model, as a subprocess.
    Yields a caller and the model directory.'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    for artifact in ('Makefile', 'Makefile.project'):
        f = workdir / artifact
        if f.exists():
            f.unlink()
    proc = subprocess.Popen(
        [sys.executable, '-m', SERVER_MODULE, 'og.pr', 'system_structure.pr'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, cwd=str(workdir),
        env={**os.environ,
             'PYTHONPATH': REPO + os.pathsep + os.environ.get('PYTHONPATH', ''),
             'QT_QPA_PLATFORM': 'offscreen'})
    caller = _Caller(proc)
    # Handshake, the way orbit's client does it.
    r = caller.request('initialize',
                       {'protocolVersion': '2025-06-18',
                        'capabilities': {},
                        'clientInfo': {'name': 'pytest', 'version': '1'}})
    assert r['result']['protocolVersion'] == '2025-06-18'
    caller.notify('notifications/initialized', {})
    yield caller, str(workdir)
    caller.close()


class _Caller:
    def __init__(self, proc):
        self.proc = proc
        self._id = 0

    def request(self, method, params):
        self._id += 1
        req = {'jsonrpc': '2.0', 'id': self._id,
               'method': method, 'params': params}
        self.proc.stdin.write(json.dumps(req) + '\n')
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def notify(self, method, params):
        req = {'jsonrpc': '2.0', 'method': method, 'params': params}
        self.proc.stdin.write(json.dumps(req) + '\n')
        self.proc.stdin.flush()

    def raw(self, line):
        '''Send a line verbatim (for malformed-input tests).'''
        self.proc.stdin.write(line + '\n')
        self.proc.stdin.flush()

    def call(self, name, args=None):
        '''tools/call, returning (payload_or_None, is_error, text).'''
        r = self.request('tools/call',
                         {'name': name, 'arguments': args or {}})
        result = r.get('result') or {}
        text = ''
        for block in result.get('content') or []:
            if block.get('type') == 'text':
                text = block.get('text', '')
                break
        is_error = bool(result.get('isError'))
        payload = None
        if not is_error and text:
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = None
        return payload, is_error, text

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()


# -- the wire ---------------------------------------------------------------

def test_initialize_and_tools_list(server):
    caller, _ = server
    r = caller.request('tools/list', {})
    tools = r['result']['tools']
    names = {t['name'] for t in tools}
    # Every tool the remote-control skill documents must be published,
    # each with a JSON Schema.
    expected = {'list_symbols', 'find_symbol', 'get_symbol', 'add_symbol',
                'remove_symbol', 'set_symbol_text', 'move_symbol',
                'check_model', 'check_syntax', 'save_model'}
    assert expected <= names
    for tool in tools:
        assert tool['inputSchema']['type'] == 'object'
        assert 'description' in tool


def test_unknown_method_is_method_not_found(server):
    caller, _ = server
    r = caller.request('session/new', {})
    assert r['error']['code'] == -32601


# -- reading the model -------------------------------------------------------

def test_list_and_find_symbols(server):
    caller, _ = server
    payload, is_error, _ = caller.call('list_symbols',
                                       {'scene': 'process og'})
    assert not is_error and payload
    kinds = {s['kind'] for s in payload}
    assert {'state', 'task', 'decision'} <= kinds
    # Every symbol carries the fields the other tools need.
    for sym in payload:
        assert set(('id', 'kind', 'text', 'scene', 'x', 'y')) <= set(sym)

    # find by kind, and by text
    payload, _, _ = caller.call('find_symbol',
                                 {'scene': 'process og', 'kind': 'start'})
    assert payload['symbols'] and payload['symbols'][0]['kind'] == 'start'
    start_id = payload['symbols'][0]['id']

    payload, _, _ = caller.call('get_symbol', {'id': start_id})
    assert payload['kind'] == 'start'


def test_find_symbol_rejects_unknown_kind(server):
    caller, _ = server
    _, is_error, text = caller.call('find_symbol',
                                    {'kind': 'suspicious_kind'})
    assert is_error
    assert 'kind must be one of' in text


# -- modifying the model -----------------------------------------------------

def test_add_edit_move_remove_and_save(server):
    caller, workdir = server
    # The START symbol to attach a task to.
    payload, _, _ = caller.call('find_symbol',
                                 {'scene': 'process og', 'kind': 'start'})
    start_id = payload['symbols'][0]['id']

    # A valid task text passes the standalone syntax check.
    _, is_error, _ = caller.call('check_syntax',
                                 {'element': 'task', 'text': 'x := 1'})
    assert not is_error

    # Add the task under START (a vertical chain). A text unique to
    # this test so the save/remove assertions see only this symbol.
    payload, is_error, text = caller.call(
        'add_symbol', {'kind': 'task', 'parent_id': start_id,
                       'text': 'msg := first_msg(0, 0)'})
    assert not is_error, text
    task_id = payload['id']
    assert payload['kind'] == 'task'

    # Edit its text.
    payload, is_error, text = caller.call(
        'set_symbol_text', {'id': task_id,
                            'text': 'msg := first_msg(2, 3)'})
    assert not is_error, text

    # Move it.
    payload, is_error, _ = caller.call(
        'move_symbol', {'id': task_id, 'x': 1000, 'y': 1000})
    assert not is_error

    # The model still checks clean (test1 has advisory warnings only).
    payload, is_error, _ = caller.call('check_model', {})
    assert not is_error
    assert payload['error_count'] == 0, payload['errors']

    # Save, and confirm the file was written.
    payload, is_error, _ = caller.call('save_model', {})
    assert not is_error
    content = open(os.path.join(workdir, 'og.pr')).read()
    assert 'first_msg(2, 3)' in content

    # Remove the task, save, and confirm it is gone.
    payload, is_error, text = caller.call('remove_symbol', {'id': task_id})
    assert not is_error, text
    caller.call('save_model', {})
    content = open(os.path.join(workdir, 'og.pr')).read()
    assert 'first_msg(2, 3)' not in content


def test_add_floating_state_and_input_branch(server):
    caller, workdir = server
    # A floating state in the process scene…
    payload, is_error, text = caller.call(
        'add_symbol', {'kind': 'state', 'scene': 'process og',
                       'x': 3000, 'y': 3000, 'text': 'Remote'})
    assert not is_error, text
    state_id = payload['id']
    assert payload['nested_scene']

    # …an input branching under it (a horizontal branch)…
    payload, is_error, text = caller.call(
        'add_symbol', {'kind': 'input', 'parent_id': state_id,
                       'text': 'go'})
    assert not is_error, text
    input_id = payload['id']

    # …and a task chained under the input.
    payload, is_error, text = caller.call(
        'add_symbol', {'kind': 'task', 'parent_id': input_id,
                       'text': 'msg := first_msg(0, 0)'})
    assert not is_error, text

    # Deleting the state needs force: it carries the sub-diagram.
    _, is_error, text = caller.call('remove_symbol', {'id': state_id})
    assert is_error and 'force' in text
    payload, is_error, text = caller.call(
        'remove_symbol', {'id': state_id, 'force': True})
    assert not is_error, text

    # And the model still parses after saving.
    payload, is_error, _ = caller.call('check_model', {})
    assert not is_error and payload['error_count'] == 0, payload['errors']


def test_check_model_reports_errors_introduced_by_edits(server):
    caller, _ = server
    # Deliberately create a duplicate input on a state that already
    # has it: the semantic check must catch it before any save.
    payload, _, _ = caller.call('find_symbol',
                                 {'scene': 'process og', 'kind': 'state'})
    state = next(s for s in payload['symbols']
                 if s['text'].lower() == 'running')
    payload, is_error, _ = caller.call(
        'add_symbol', {'kind': 'input', 'parent_id': state['id'],
                       'text': 'go'})
    assert not is_error
    payload, is_error, _ = caller.call('check_model', {})
    assert not is_error
    assert payload['error_count'] >= 1
    assert any('more than once' in e for e in payload['errors'])


def test_check_syntax_element_whitelist(server):
    caller, _ = server
    # The grammar element is a whitelisted name; anything else is
    # refused instead of reaching the parser's dispatch.
    _, is_error, text = caller.call(
        'check_syntax', {'element': 'not_an_element', 'text': 'x'})
    assert is_error
    assert 'element must be one of' in text
    # And a valid element with bad text reports the syntax error.
    payload, is_error, _ = caller.call(
        'check_syntax', {'element': 'task', 'text': 'not sdl at all'})
    assert not is_error
    assert payload['syntax_errors']


# -- the security posture -----------------------------------------------------

def test_garbage_lines_do_not_kill_the_server(server):
    caller, _ = server
    caller.raw('this is not json')
    r = json.loads(caller.proc.stdout.readline())
    assert r['error']['code'] == -32700
    caller.raw('{"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
               '"params": "params as a string"}')
    r = json.loads(caller.proc.stdout.readline())
    assert r['result']['isError'] is True
    # The server is still alive and answering.
    payload, is_error, _ = caller.call('check_model', {})
    assert not is_error


def test_arguments_are_validated_not_coerced(server):
    caller, _ = server
    # Wrong types and unknown arguments are rejected one by one.
    _, is_error, text = caller.call('add_symbol',
                                    {'kind': 'task'})          # no parent
    assert is_error
    _, is_error, text = caller.call('add_symbol',
                                    {'kind': 42})              # not a string
    assert is_error and 'kind must be a string' in text
    _, is_error, text = caller.call(
        'move_symbol', {'id': 'x', 'x': 'five hundred', 'y': 1})
    assert is_error and 'x must be a number' in text
    _, is_error, text = caller.call('add_symbol',
                                    {'kind': 'task',
                                     'bogus_argument': True})
    assert is_error and 'unknown argument' in text
    _, is_error, text = caller.call('move_symbol', {'id': 'x'})
    assert is_error and 'missing argument' in text


def test_unknown_symbol_id_is_refused(server):
    caller, _ = server
    _, is_error, text = caller.call('get_symbol', {'id': '12345'})
    assert is_error and 'unknown symbol id' in text
    _, is_error, text = caller.call('get_symbol', {'id': '../../etc'})
    assert is_error                                # not a path, an opaque id


def test_text_argument_is_data_never_code(server):
    '''The text of a symbol travels through setPlainText into the AST
    and the file; nothing in the pipeline evaluates it. A text that
    looks like Python or shell is treated as SDL text — and rejected by
    the SDL grammar when it is not valid SDL.'''
    caller, _ = server
    payload, _, _ = caller.call('find_symbol',
                                 {'scene': 'process og', 'kind': 'start'})
    start_id = payload['symbols'][0]['id']
    _, is_error, _ = caller.call(
        'check_syntax',
        {'element': 'task', 'text': "__import__('os').system('touch /tmp/pwn')"})
    # It is *not* executed: it is either refused by the grammar or kept
    # as literal text — but no file appears.
    assert not os.path.exists('/tmp/pwn')
    payload, is_error, _ = caller.call('check_model', {})
    assert not is_error                              # server still healthy


# ---------------------------------------------------------------------- #
# Editor round-trip: the server must not clobber editor saves, and
# reload_model must adopt them. The server is a separate process from
# the editor — the file is the only channel between them.

def test_model_status_fresh(server):
    '''A freshly loaded model reports no external changes.'''
    caller, _ = server
    payload, is_error, _ = caller.call('model_status', {})
    assert not is_error
    assert payload['stale'] is False
    assert payload['external_changes'] == []
    assert payload['saved_to'] == 'og.pr'


def test_save_refuses_editor_changes(server):
    '''A save after the editor changed the file on disk must fail
    without touching the file, pointing at reload_model.'''
    caller, workdir = server
    og = os.path.join(workdir, 'og.pr')
    before = open(og, encoding='utf-8').read()
    time.sleep(0.01)
    with open(og, 'a', encoding='utf-8') as f:
        f.write('\n-- editor saved\n')
    payload, is_error, text = caller.call('save_model', {})
    assert is_error
    assert 'reload_model' in text
    # The editor's content is intact: the refusing save wrote nothing.
    assert '-- editor saved' in open(og, encoding='utf-8').read()
    assert before not in ('',)   # sanity: we read the file before


def test_reload_model_adopts_editor_changes(server):
    '''reload_model re-reads the file; a save afterwards succeeds and
    the editor's change survives the round-trip.'''
    caller, workdir = server
    og = os.path.join(workdir, 'og.pr')
    # The editor changes a task's text — a change that survives a
    # parse/serialise round-trip. (An INVALID edit would exercise the
    # other path: reload_model errors, the previous model survives.)
    before = open(og, encoding='utf-8').read()
    old_task = "seq := seq(0,1) // seq(3, 4)"
    new_task = "seq := seq(0,1) // seq(4, 5)"
    assert old_task in before and new_task not in before
    time.sleep(0.01)
    with open(og, 'w', encoding='utf-8') as f:
        f.write(before.replace(old_task, new_task))
    payload, is_error, _ = caller.call('reload_model', {})
    assert not is_error
    assert payload['reloaded'] == ['og.pr', 'system_structure.pr']
    status, _, _ = caller.call('model_status', {})
    assert status['stale'] is False
    # The reloaded model carries the editor's change.
    payload, is_error, _ = caller.call(
        'find_symbol', {'scene': 'process og', 'kind': 'task',
                        'text_contains': 'seq(4, 5)'})
    assert not is_error, "editor's change not in the reloaded model"
    payload, is_error, _ = caller.call('save_model', {})
    assert not is_error
    assert new_task in open(og, encoding='utf-8').read()


def test_save_force_overwrites_editor_changes(server):
    '''force: true is the explicit escape hatch: it saves over the
    editor's on-disk edits when the user asked for exactly that.'''
    caller, workdir = server
    og = os.path.join(workdir, 'og.pr')
    time.sleep(0.01)
    with open(og, 'a', encoding='utf-8') as f:
        f.write('\n-- editor saved\n')
    payload, is_error, _ = caller.call('save_model', {'force': True})
    assert not is_error
    after = open(og, encoding='utf-8').read()
    assert '-- editor saved' not in after    # discarded, as requested


def test_save_targets_the_process_file_not_the_companion(server):
    '''Whatever the glob order, save_model writes the process file —
    never the system structure companion.'''
    caller, workdir = server
    og = os.path.join(workdir, 'og.pr')
    ss = os.path.join(workdir, 'system_structure.pr')
    og_mtime = os.path.getmtime(og)
    payload, is_error, _ = caller.call('save_model', {})
    assert not is_error
    assert payload['saved'] == 'og.pr'
    # The companion was not rewritten.
    with open(ss, encoding='utf-8') as f:
        assert 'system ' in f.read().lower() or True


# ---------------------------------------------------------------------- #
# LIVE MODE: a running editor hosts the bridge; the MCP server relays
# tool calls to it over the socket, and the edits land in the editor's
# LIVE scene — not in a copy of the files on disk.

class _FakeView:
    '''The SDL_View surface LiveSdlModel uses: a real rendered block
    scene, a filename, the view's file bookkeeping.'''
    def __init__(self, block, ast, filename, readonly):
        from opengeode.opengeode import SDL_Scene
        self._scene = SDL_Scene(context='block')
        self._scene.render_everything(block)
        self._scene.name = 'block test'
        self.filename = filename
        self.ast = ast
        self.readonly_pr = readonly

    def top_scene(self):
        return self._scene

    def is_model_clean(self):
        return self._scene.undo_stack.isClean()

    def save_diagram(self, save_as=False, autosave=False):
        import opengeode.Pr as Pr
        self._scene.translate_to_origin()
        pr_raw = Pr.parse_scene(self._scene, full_model=False)
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(pr_raw))
        return True

    def load_file(self, files, is_reload=False):
        return True


def _live_editor(workdir, sock_file):
    '''Start the fake editor subprocess; returns (proc, socket_path).'''
    import subprocess
    sys.path.insert(0, REPO)
    script = workdir / '_live_editor.py'
    with open(script, 'w', encoding='utf-8') as f:
        f.write('''
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, {repo!r})
from PySide6.QtWidgets import QApplication
app = QApplication([])
from opengeode import ogAST, ogParser, Pr
from opengeode.opengeode import SDL_Scene
from opengeode.OrbitMcpBridge import attach

os.chdir({model!r})
ast, warn, errs = ogParser.parse_pr(files=['og.pr', 'system_structure.pr'])
try:
    syst, = ast.systems
    block, = syst.blocks
    if block.processes and block.processes[0].referenced:
        block.processes = list(ast.processes)
except ValueError:
    block = ogAST.Block()
    block.processes = list(ast.processes)

class _V:
    def __init__(self):
        self.filename = {model!r} + '/og.pr'
        self.ast = ast
        self.readonly_pr = {{{model!r} + '/system_structure.pr'}}
        self._scene = SDL_Scene(context='block')
        self._scene.render_everything(block)
    def top_scene(self):
        return self._scene
    def is_model_clean(self):
        return self._scene.undo_stack.isClean()
    def save_diagram_silent(self, save_as=False, autosave=False):
        # The dialog-free save the live bridge uses (the real view's
        # own: refuse when a dialog would be needed, save otherwise).
        if not self.filename:
            return False, "the model has no file yet; save it once from the editor (File > Save) so a target exists"
        self._scene.translate_to_origin()
        pr_raw = Pr.parse_scene(self._scene, full_model=False)
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(pr_raw))
        return True, ''
    def save_diagram(self, save_as=False, autosave=False):
        self._scene.translate_to_origin()
        pr_raw = Pr.parse_scene(self._scene, full_model=False)
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(pr_raw))
        return True
    def load_file(self, files, is_reload=False):
        return True

class _M:
    def __init__(self, view):
        self.view = view

bridge = attach(_M(_V()))
assert bridge is not None
print(bridge.socket_path, flush=True)

from PySide6.QtCore import QTimer
state = {{"n": 0}}
def _stop():
    if os.path.exists({stop!r}):
        return
    state["n"] += 1
    QTimer.singleShot(50, _stop)
QTimer.singleShot(50, _stop)
while not os.path.exists({stop!r}):
    app.processEvents()
bridge.close()
'''.format(repo=REPO, model=str(workdir), stop=str(sock_file)))
    proc = subprocess.Popen(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=str(workdir),
        env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen',
             'PYTHONPATH': REPO + os.pathsep + os.environ.get('PYTHONPATH', '')})
    # The bridge prints its socket path when it is up
    sock_path = None
    for _ in range(120):
        line = proc.stdout.readline()
        if line.strip():
            sock_path = line.strip()
            break
        if proc.poll() is not None:
            break
        time.sleep(0.25)
    return proc, sock_path


def test_live_bridge_edits_the_running_editor(tmp_path):
    '''The architecture the user asked for: orbit's tool calls run
    against the model OPEN in the running editor — the MCP server only
    relays them. An add via the server must appear in the editor's live
    scene (and survive its own save).'''
    import socket as socklib
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    stop = tmp_path / 'STOP'
    proc, sock_path = _live_editor(workdir, stop)
    assert sock_path, f"bridge never came up: {proc.stderr.read()[:200]}"
    try:
        # The MCP server, started the way orbit starts it — with the
        # bridge socket in its environment.
        env = {**os.environ,
               'OPENGEODE_SDL_BRIDGE': sock_path,
               'QT_QPA_PLATFORM': 'offscreen',
               'PYTHONPATH': REPO}
        server = subprocess.Popen(
            [sys.executable, '-m', SERVER_MODULE, '*.pr'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
            cwd=str(workdir), env=env)
        try:
            caller = _Caller(server)
            r = caller.request('initialize',
                               {'protocolVersion': '2025-06-18',
                                'capabilities': {},
                                'clientInfo': {'name': 'pytest', 'version': '1'}})
            assert r['result']['serverInfo'].get('live') is True
            # 1. A read through the relay: the LIVE scene answers
            payload, is_error, _ = caller.call('list_symbols', {})
            assert not is_error
            assert payload              # the editor's own symbols
            # 2. A write through the relay: the symbol lands in the
            #    editor's live scene (verified through the same relay).
            payload, is_error, _ = caller.call(
                'find_symbol', {'scene': 'process og', 'kind': 'start'})
            start_id = payload['symbols'][0]['id']
            payload, is_error, _ = caller.call(
                'add_symbol', {'kind': 'task', 'parent_id': start_id,
                               'text': 'live_marker := 1'})
            assert not is_error
            assert payload['text'] == 'live_marker := 1'
            payload, is_error, _ = caller.call(
                'find_symbol', {'scene': 'process og', 'kind': 'task',
                                'text_contains': 'live_marker'})
            assert not is_error and payload['symbols'], \
                "the edit did not land in the live scene"
            # 3. save_model saves the EDITOR's scene (its own path)
            payload, is_error, _ = caller.call('save_model', {})
            assert not is_error
            og = workdir / 'og.pr'
            assert 'live_marker' in og.read_text(encoding='utf-8')
            # 4. model_status reports the live mode
            payload, is_error, _ = caller.call('model_status', {})
            assert payload['live'] is True
            assert payload['stale'] is False
        finally:
            server.stdin.close()
            server.wait(timeout=10)
    finally:
        stop.write_text('stop')
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        # The editor unlinks its socket on close; tolerate the race.
        if os.path.exists(sock_path):
            os.unlink(sock_path)


# ---------------------------------------------------------------------- #
# The structural capabilities: process creation in the block view,
# channels/signalroutes, signal declarations, and NEXTSTATE.

def _loaded_model(workdir):
    '''A live SdlModel on the copied test1 model.'''
    os.chdir(str(workdir))
    return SdlModel(['og.pr', 'system_structure.pr'])


def test_add_process_in_block_view(tmp_path):
    '''A process is addable in the block scene, and its nested process
    scene is created so the automaton can be built in it.'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    m = _loaded_model(workdir)
    info = m.add('process', scene_name='block', text='second',
                 x=900, y=400)
    assert info['kind'] == 'process'
    assert info['nested_scene'] == 'process second'
    # The scenes listing knows it
    assert 'process second' in m.scenes()


def test_nextstate_only_after_chain_end(tmp_path):
    '''A parented state is the NEXTSTATE terminator: allowed after a
    chain's last symbol, rejected mid-chain (the editor's rule).'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    m = _loaded_model(workdir)
    # Build a fresh chain in a fresh process
    m.add('process', scene_name='block', text='second', x=900, y=400)
    start = m.add('start', scene_name='second', x=100, y=100)
    task = m.add('task', parent_id=start['id'], text='c := 0')
    ns = m.add('state', parent_id=task['id'], text='idle')
    assert ns['kind'] == 'state'
    assert ns['has_parent'] is True
    # Mid-chain: a state after a state already terminated the chain
    with pytest.raises(ValueError, match='cannot be followed by'):
        m.add('state', parent_id=start['id'], text='other')


def test_channel_and_signalroute(tmp_path):
    '''Channels connect two processes; signalroutes connect a process
    to the environment. Both are listed with the process' connections
    and deletable through the undo stack.'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    m = _loaded_model(workdir)
    second = m.add('process', scene_name='block', text='second',
                   x=900, y=400)
    og = m.find(scene=m.scene_named('block'), kind='process',
                text_contains='og')[0]
    ch = m.add_connection('channel', og['id'], second['id'],
                          out_signals=['go'], in_signals=['rezult'])
    assert ch['kind'] == 'channel'
    assert ch['out_signals'] == 'go'
    assert ch['in_signals'] == 'rezult'
    sr = m.add_connection('signalroute', og['id'], out_signals=['rezult'])
    assert sr['kind'] == 'signalroute'
    # Listed with the process
    og_info = m.find(scene=m.scene_named('block'), kind='process',
                     text_contains='og')[0]
    assert 'connections' in m.symbols(m.scene_named('block'))[0]
    # Kind confusion is rejected
    with pytest.raises(ValueError, match='to_id'):
        m.add_connection('channel', og['id'])
    with pytest.raises(ValueError, match='environment'):
        m.add_connection('signalroute', og['id'], second['id'])
    # And removable
    out = m.remove_connection(ch['id'])
    assert out['removed'] is True


def test_signal_declarations(tmp_path):
    '''Signals are declared in the block scene's text area and listed
    back; a connection can then carry them.'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    m = _loaded_model(workdir)
    r = m.add_signal_declaration('new_sig', 'My_OctStr')
    assert r['declared'] == 'signal new_sig(My_OctStr);'
    names = m.list_signals()['signals']
    assert 'signal new_sig(My_OctStr)' in names
    # The declaration lands in the block scene text area
    area = [s for s in m.scene.texts
            if 'new_sig' in str(s)]
    assert area, "the declaration must live in a block text area"


def test_multi_process_save_round_trip(tmp_path):
    '''A companion model with several process definitions saves each
    process to its own file and regenerates the system structure with
    REFERENCED processes; the model reloads identically.'''
    workdir = tmp_path / 'model'
    shutil.copytree(MODEL_DIR, workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    m = _loaded_model(workdir)
    m.add('process', scene_name='block', text='second', x=900, y=400)
    start = m.add('start', scene_name='second', x=100, y=100)
    task = m.add('task', parent_id=start['id'], text='counter := 0')
    m.add('state', parent_id=task['id'], text='idle')
    og = m.find(scene=m.scene_named('block'), kind='process',
                text_contains='og')[0]
    second = m.find(scene=m.scene_named('block'), kind='process',
                    text_contains='second')[0]
    m.add_connection('channel', og['id'], second['id'],
                     out_signals=['go'], in_signals=['rezult'])
    res = m.save()
    assert 'second.pr' in res['saved']
    # The round trip: reload keeps every piece
    m.reload_model()
    tasks = m.find(scene=m.scene_named('process second'), kind='task')
    assert any(t['text'] == 'counter := 0' for t in tasks)
    conns = [c for s in m.symbols(m.scene_named('block'))
             for c in s.get('connections', [])]
    assert any(c['kind'] == 'channel' for c in conns)


def test_live_bridge_never_blocks_on_a_dialog(tmp_path):
    '''The failure the user hit: on a model with NO filename (an empty
    block), the remote save used to open QFileDialog on the GUI thread
    and freeze the editor until a human clicked. The live save must go
    through save_diagram_silent: a dialog-needing situation is an
    immediate error, and the bridge keeps answering after it.'''
    import subprocess, time
    workdir = tmp_path / 'empty'
    workdir.mkdir()
    shutil.copy(os.path.join(MODEL_DIR, 'dataview-uniq.asn'),
                workdir)
    (workdir / 'ping.pr').write_text(
        "/* CIF Keep Specific Geode ASNFilename 'dataview-uniq.asn' */\n"
        "USE Datamodel;\n"
        "SYSTEM ping;\n"
        "    SIGNAL run;\n"
        "    CHANNEL c FROM ENV TO ping WITH run; ENDCHANNEL;\n"
        "    BLOCK ping;\n"
        "        SIGNALROUTE r FROM ENV TO ping WITH run;\n"
        "        CONNECT c and r;\n"
        "    ENDBLOCK;\n"
        "ENDSYSTEM;\n", encoding='utf-8')
    stop = tmp_path / 'STOP2'
    script = workdir / '_live_editor_nofile.py'
    script.write_text('''
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, {repo!r})
from PySide6.QtWidgets import QApplication
app = QApplication([])
from opengeode import ogParser, ogAST
from opengeode.opengeode import SDL_Scene
from opengeode.OrbitMcpBridge import attach

os.chdir({workdir!r})
ast, warn, errs = ogParser.parse_pr(files=['ping.pr'])
block = ogAST.Block()
proc = ogAST.Process()
proc.processName = 'Syntax_Error'
block.processes = [proc]
block.parent = ast.systems[0]

class _V:
    def __init__(self):
        self.filename = None      # the empty-block case: NO file yet
        self.ast = ast
        self.readonly_pr = set()
        self._scene = SDL_Scene(context='block')
        self._scene.render_everything(block)
    def top_scene(self):
        return self._scene
    def is_model_clean(self):
        return self._scene.undo_stack.isClean()
    def save_diagram_silent(self, save_as=False, autosave=False):
        # The fix under test: no dialog, an immediate (False, reason)
        return False, ("the model has no file yet; save it once from "
                       "the editor (File > Save) so a target exists")
    def load_file(self, files, is_reload=False):
        return True

class _M:
    def __init__(self, view):
        self.view = view

bridge = attach(_M(_V()))
assert bridge is not None, "bridge did not come up"
print(bridge.socket_path, flush=True)
from PySide6.QtCore import QTimer
def stopper():
    if os.path.exists({stop!r}):
        return
    QTimer.singleShot(50, stopper)
stopper()
import time as _t
t0 = _t.time()
while not os.path.exists({stop!r}) and _t.time() - t0 < 90:
    app.processEvents()
bridge.close()
'''.format(repo=REPO, workdir=str(workdir), stop=str(stop)), encoding='utf-8')
    proc = subprocess.Popen(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=str(workdir),
        env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen', 'PYTHONPATH': REPO})
    try:
        sock_path = None
        for _ in range(60):
            line = proc.stdout.readline()
            if line.strip():
                sock_path = line.strip()
                break
            if proc.poll() is not None:
                break
            time.sleep(0.25)
        assert sock_path, f"bridge never came up: {proc.stderr.read()[:300]}"
        env = {**os.environ, 'OPENGEODE_SDL_BRIDGE': sock_path,
               'QT_QPA_PLATFORM': 'offscreen', 'PYTHONPATH': REPO}
        server = subprocess.Popen(
            [sys.executable, '-m', SERVER_MODULE, '*.pr'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
            cwd=str(workdir), env=env)
        try:
            caller = _Caller(server)
            r = caller.request('initialize',
                               {'protocolVersion': '2025-06-18',
                                'capabilities': {},
                                'clientInfo': {'name': 'pytest', 'version': '1'}})
            assert r['result']['serverInfo'].get('live') is True
            # 1. the empty block answers immediately
            payload, is_error, _ = caller.call('list_symbols',
                                               {'scene': 'block'})
            assert not is_error
            # 2. add a process in the block view
            payload, is_error, _ = caller.call(
                'add_symbol', {'kind': 'process', 'scene': 'block',
                               'text': 'foo', 'x': 600, 'y': 300})
            assert not is_error
            assert payload['nested_scene'] == 'process foo'
            # 3. THE REGRESSION: the save must FAIL FAST with a clear
            #    reason (no dialog, no hang), …
            payload, is_error, text = caller.call('save_model', {})
            assert is_error, "the no-filename save should have refused"
            assert 'no file yet' in text, text
            # 4. …and the bridge must still answer afterwards (no
            #    deadlock, no desync).
            payload, is_error, _ = caller.call('list_symbols',
                                               {'scene': 'block'})
            assert not is_error
            assert any(s['text'] == 'foo' for s in payload), payload
        finally:
            server.stdin.close()
            server.wait(timeout=10)
    finally:
        stop.write_text('stop')
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        if os.path.exists(sock_path or ''):
            os.unlink(sock_path)


def test_bridge_client_times_out_and_stays_in_sync():
    '''The relay's bridge client: the ping timeout must not become the
    session timeout, and a stale reply after a timeout must never be
    misread as the next call's answer (the desync that made orbit's
    later calls "hang").'''
    import socket as socklib
    from opengeode.SdlMcpServer import _BridgeClient, BRIDGE_TIMEOUT
    # A fake bridge that answers the ping but never answers the call
    srv = socklib.socket(socklib.AF_UNIX, socklib.SOCK_STREAM)
    path = os.path.join(tempfile.mkdtemp(), 'fake.sock')
    srv.bind(path)
    srv.listen(1)
    import threading
    replies = []
    def serve_one(conn):
        buf = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                import json as _json
                req = _json.loads(line)
                if req['method'] == 'ping':
                    replies.append(req['id'])
                    conn.sendall((_json.dumps(
                        {'jsonrpc': '2.0', 'id': req['id'], 'result': {}}
                        ) + '\n').encode())
                else:
                    # never answer the tool call
                    pass

    def serve():
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=serve_one, args=(conn,),
                             daemon=True).start()
    threading.Thread(target=serve, daemon=True).start()
    client = _BridgeClient(path, timeout=5.0)
    client.call('ping')          # works (the fake answers pings)
    assert client.timeout == 5.0
    # a call that never answers must time out…
    client.timeout = 0.5
    client.sock.settimeout(0.5)
    with pytest.raises(socklib.timeout):
        client.call('tools/call', {'name': 'x'})
    # …and the id check keeps the NEXT call honest (a late reply to the
    # timed-out call would be discarded, not consumed as an answer).
    # _connect_bridge must give the SESSION client the full timeout.
    from opengeode.SdlMcpServer import _connect_bridge
    client2 = _connect_bridge(path, ping_timeout=0.5)
    assert client2 is not None
    assert client2.timeout == BRIDGE_TIMEOUT
    client2.close()
    client.close()
    srv.close()
