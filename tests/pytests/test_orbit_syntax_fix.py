#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Tests for the orbit "Auto fix" of syntax errors (OrbitSyntaxFix).

The module asks orbit — the same agent the chat panel talks to, with the same
bundled SDL skill — for a corrected version of a symbol whose text failed to
parse, then offers it to the user. These tests cover the parts that do not need
a full editor: independence from orbit being present, the prompt/extraction
helpers, one real round-trip through the fake orbit agent, and the apply path
with the review and progress dialogs stubbed out.
'''

import pytest

# orbit_acp is optional for OpenGEODE; these tests exercise its API, so require
# it (and PySide6 for the Qt objects).
orbit_acp = pytest.importorskip('orbit_acp')
pytest.importorskip('PySide6')

import opengeode.OrbitSyntaxFix as osf

from PySide6.QtWidgets import QWidget

# The same stand-in for `orbit acp` the chat-panel tests drive.
FAKE = "python3 -m orbit_acp.testing.fake_agent"


@pytest.fixture(scope='module', autouse=True)
def qapp():
    '''A QApplication for the whole module. It is autouse: it must exist before
    any test runs, and it must be a QApplication (not a bare QCoreApplication),
    or building the view widget would abort the process.'''
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# --------------------------------------------------------------------------
# Availability: the whole feature is hidden when orbit is not reachable.
# --------------------------------------------------------------------------

def test_unavailable_when_orbit_acp_is_not_importable(monkeypatch):
    '''No orbit_acp (or no orbit): auto_fix_available is False, so the caller
    shows no UI.'''
    monkeypatch.setattr(osf, 'orbit_acp_available', lambda: False)
    assert osf.auto_fix_available() is False


def test_unavailable_when_the_availability_check_raises(monkeypatch):
    '''A broken orbit install must degrade to "not available", never to an
    exception that would block the editor.'''
    def boom():
        raise RuntimeError('orbit is misconfigured')
    monkeypatch.setattr(osf, 'orbit_acp_available', boom)
    assert osf.auto_fix_available() is False


def test_available_when_orbit_is_present(monkeypatch):
    monkeypatch.setattr(osf, 'orbit_acp_available', lambda: True)
    assert osf.auto_fix_available() is True


# --------------------------------------------------------------------------
# Prompt construction and answer extraction (pure functions).
# --------------------------------------------------------------------------

def test_build_question_carries_construct_text_and_errors():
    q = osf._build_question("task", "x := ;", ["line 3:5 expression expected"])
    assert "task" in q
    assert "x := ;" in q
    assert "expression expected" in q
    # The agent is asked for a single fenced block and nothing else.
    assert "fenced code block" in q


def test_build_question_handles_missing_errors():
    q = osf._build_question("output", "hello", [])
    assert "(no detail given)" in q


def test_extract_code_takes_the_fenced_block():
    assert osf._extract_code("```\nx := 1;\n```") == "x := 1;"


def test_extract_code_drops_the_language_tag():
    assert osf._extract_code("```sdl\nx := 1;\n```") == "x := 1;"


def test_extract_code_takes_the_first_block_only():
    answer = "Here:\n```\nx := 1;\n```\nAnd also ```\ny := 2;\n```"
    assert osf._extract_code(answer) == "x := 1;"


def test_extract_code_without_a_fence_returns_the_answer():
    assert osf._extract_code("  x := 1;  ") == "x := 1;"


def test_extract_code_of_empty_answer_is_empty():
    assert osf._extract_code("") == ""
    assert osf._extract_code(None) == ""


# --------------------------------------------------------------------------
# The worker: a real round-trip through the fake orbit agent.
# --------------------------------------------------------------------------

def test_worker_asks_orbit_and_reports_the_answer(qapp, monkeypatch):
    '''_OrbitAsker opens a conversation, stages the SDL skill, asks, and emits
    the answer text. Driven against orbit_acp's fake agent, with the same
    QThread + QEventLoop shape auto_fix_symbol uses.'''
    from PySide6.QtCore import QEventLoop, QThread, QTimer
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)

    question = osf._build_question("task", "x := ;", ["expression expected"])
    thread = QThread()
    asker = osf._OrbitAsker(question, ".")
    asker.moveToThread(thread)
    out = {}
    loop = QEventLoop()

    def on_done(payload):
        out['answer'], out['error'] = payload
        loop.quit()

    thread.started.connect(asker.run)
    asker.done.connect(on_done)
    asker.done.connect(thread.quit)
    QTimer.singleShot(30000, loop.quit)         # safety net
    thread.start()
    loop.exec()
    thread.wait(5000)

    assert out.get('error') is None, out
    assert out.get('answer'), 'the fake agent answered nothing'


# --------------------------------------------------------------------------
# The apply path, with the progress and review dialogs stubbed out.
# --------------------------------------------------------------------------

class _FakeText:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value
    def setPlainText(self, value):
        self.value = value
    def try_resize(self):
        pass


class _FakeScene:
    '''Just enough of an SDL_Scene: syntax_errors(), the re-check after a fix.'''
    def __init__(self, errors_after=()):
        self._errors_after = list(errors_after)
        self.checked = 0
    def syntax_errors(self, symbol):
        self.checked += 1
        return list(self._errors_after)


class _FakeSymbol:
    def __init__(self, text, construct="task", scene=None):
        self.text = _FakeText(text)
        self.common_name = construct
        self._scene = scene if scene is not None else _FakeScene()
    def scene(self):
        return self._scene


class _FakeView(QWidget):
    '''Just enough of an SDL_View for auto_fix_symbol: a model filename. It is
    a real QWidget (the view is a QGraphicsView, and the message boxes take a
    QWidget parent). The syntax re-check goes through symbol.scene(), not the
    view — this mirrors the real split (syntax_errors lives on SDL_Scene).'''
    def __init__(self, filename):
        super().__init__()
        self.filename = filename


def _stub_dialogs(monkeypatch, accept=True):
    '''Replace the modal progress and review dialogs, and QMessageBox.warning,
    with objects that return immediately: the test drives the logic, not Qt's
    event loop.'''
    class _Progress:
        def __init__(self, *a, **k):
            self.canceled = _NullSignal()
        def setWindowTitle(self, *a): pass
        def setWindowModality(self, *a): pass
        def setMinimumDuration(self, *a): pass
        def setAutoClose(self, *a): pass
        def setAutoReset(self, *a): pass
        def show(self): pass
        def close(self): pass
        def wasCanceled(self): return False
    class _NullSignal:
        def connect(self, *a): pass
    class _Review:
        def __init__(self, *a, **k): pass
        def exec(self):
            from PySide6.QtWidgets import QDialog
            return QDialog.Accepted if accept else QDialog.Rejected
    class _MessageBox:
        @staticmethod
        def warning(*a, **k):
            return None
    monkeypatch.setattr(osf, 'QProgressDialog', _Progress)
    monkeypatch.setattr(osf, '_ReviewDialog', _Review)
    monkeypatch.setattr(osf, 'QMessageBox', _MessageBox)


def test_apply_replaces_the_text_when_orbit_fixes_it(qapp, tmp_path, monkeypatch):
    '''orbit's correction is applied, the symbol parses, and auto_fix_symbol
    returns True (so the caller records the edit). The answer is scripted
    through a stub asker, so no agent process is needed.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    # Stub the asker to return a fixed correction without a subprocess: its
    # done signal fires as soon as run() is called.
    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd):
            super().__init__()
        def moveToThread(self, t):
            pass
        def run(self):
            self.done.emit(("```\nx := 1;\n```", None))
        def cancel(self):
            pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("x := ;")
    assert osf.auto_fix_symbol(view, symbol, ["expression expected"]) is True
    assert str(symbol.text) == "x := 1;"
    assert symbol.scene().checked >= 1


def test_cancel_leaves_the_text_untouched(qapp, tmp_path, monkeypatch):
    '''Declining the review dialog changes nothing.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=False)

    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd):
            super().__init__()
        def moveToThread(self, t): pass
        def run(self):
            self.done.emit(("```\nx := 1;\n```", None))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("x := ;")
    assert osf.auto_fix_symbol(view, symbol, ["expression expected"]) is False
    assert str(symbol.text) == "x := ;"


def test_a_suggestion_that_still_does_not_parse_is_rolled_back(qapp, tmp_path,
                                                               monkeypatch):
    '''If orbit's text still fails the parser, the original text is restored
    and False is returned: the model is never left in a worse state.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd):
            super().__init__()
        def moveToThread(self, t): pass
        def run(self):
            self.done.emit(("```\nstill broken ;\n```", None))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)
    # The re-check still reports an error.
    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("x := ;",
                         scene=_FakeScene(errors_after=["still bad"]))
    assert osf.auto_fix_symbol(view, symbol, ["expression expected"]) is False
    assert str(symbol.text) == "x := ;"


def test_empty_text_is_not_sent_to_orbit(qapp, tmp_path, monkeypatch):
    '''A symbol with no text has nothing to fix: no UI, straight to False.'''
    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("   ")
    assert osf.auto_fix_symbol(view, symbol, ["error"]) is False
