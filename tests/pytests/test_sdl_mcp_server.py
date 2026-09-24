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

import pytest

pytest.importorskip('PySide6')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SERVER_MODULE = 'opengeode.SdlMcpServer'
# A small, well-formed model: one process, states, tasks, a text area.
MODEL_DIR = os.path.join(REPO, 'tests', 'testsuite', 'test1')


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
