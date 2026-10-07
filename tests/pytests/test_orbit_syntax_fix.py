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


def test_build_question_forbids_tool_use():
    '''The prompt must keep orbit from exploring the project: given a working
    directory full of files, an agent that is not told to just rewrite the
    snippet reads/greps/searches until the timeout and answers nothing (which
    makes the feature look broken). A syntax fix is a pure text rewrite.'''
    q = osf._build_question("task", "x := ;", ["boom"])
    flat = " ".join(q.split()).lower()
    assert "do not" in flat and "use any tool" in flat
    assert "answer immediately" in flat


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


class _Messages:
    '''A stand-in for the scene's message window (QListWidget).'''
    def __init__(self):
        self.lines = []
    def addItem(self, item):
        self.lines.append(item if isinstance(item, str) else str(item))


class _FakeScene:
    '''Just enough of an SDL_Scene: syntax_errors() and a message window.

    It mirrors OpenGEODE's real rule so the tests catch the bug it caused: for
    every symbol EXCEPT a text area, a text that ends with ';' is rejected
    ("Remove the semi-colon at the end of the text.") because the generator adds
    the terminator itself. force_errors overrides the rule for the rollback
    test.'''
    def __init__(self, force_errors=()):
        self._force = list(force_errors)
        self.checked = 0
        self.messages_window = _Messages()
    def syntax_errors(self, symbol):
        self.checked += 1
        if self._force:
            return list(self._force)
        text = str(symbol.text).strip()
        if symbol.common_name != 'text_area' and text.endswith(';'):
            return ["Remove the semi-colon at the end of the text."]
        return []


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
        '''Emulates QProgressDialog: wasCanceled() is False until close() is
        called, after which it reports True (as Qt really does). Reading it
        after close() — the bug this shape guards — would look cancelled.'''
        def __init__(self, *a, **k):
            self.canceled = _NullSignal()
            self._closed = False
        def setWindowTitle(self, *a): pass
        def setWindowModality(self, *a): pass
        def setMinimumDuration(self, *a): pass
        def setAutoClose(self, *a): pass
        def setAutoReset(self, *a): pass
        def show(self): pass
        def close(self): self._closed = True
        def wasCanceled(self): return self._closed
    class _NullSignal:
        def connect(self, *a): pass
    class _Review:
        #: Which candidate the stub dialog "chooses"; None = the default (0).
        pick = 0
        last_candidates = None
        def __init__(self, parent, construct, current, proposed, candidates,
                     errors):
            _Review.last_candidates = list(candidates)
            self.chosen_text = candidates[_Review.pick]
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


def test_apply_strips_the_semicolon_orbit_adds(qapp, tmp_path, monkeypatch):
    '''The bug this guards: orbit answers with a complete SDL statement
    ('x := 1;'), but a task symbol must NOT end with ';' (the generator adds it,
    and check_syntax rejects a trailing semicolon). The fix must strip it, so
    the symbol really changes and parses. The answer is scripted through a stub
    asker, so no agent process is needed.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    # Stub the asker to return a fixed correction without a subprocess: its
    # done signal fires as soon as run() is called.
    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        answer = "```\nx := 1;\n```"
        def __init__(self, q, cwd):
            super().__init__()
        def moveToThread(self, t):
            pass
        def run(self):
            self.done.emit((_InstantAsker.answer, None))
        def cancel(self):
            pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("x := ;")           # common_name 'task'
    assert osf.auto_fix_symbol(view, symbol, ["expression expected"]) is True
    # The projected text is the parseable one: the ';' was stripped.
    assert str(symbol.text) == "x := 1"
    assert symbol.scene().syntax_errors(symbol) == []
    # A text_area keeps its semicolons: the same shape of answer, applied
    # verbatim (no stripping), so its own terminator survives.
    _InstantAsker.answer = "```\ndcl x MyInt;\n```"
    area = _FakeSymbol("dcl x MyInt", construct="text_area")
    assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "model.pr")), area,
                               ["bad"]) is True
    assert str(area.text) == "dcl x MyInt;"


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
    # The re-check always reports an error (both candidate forms fail).
    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("x := ;",
                         scene=_FakeScene(force_errors=["still bad"]))
    assert osf.auto_fix_symbol(view, symbol, ["expression expected"]) is False
    assert str(symbol.text) == "x := ;"


def test_empty_text_is_not_sent_to_orbit(qapp, tmp_path, monkeypatch):
    '''A symbol with no text has nothing to fix: no UI, straight to False.'''
    view = _FakeView(str(tmp_path / "model.pr"))
    symbol = _FakeSymbol("   ")
    assert osf.auto_fix_symbol(view, symbol, ["error"]) is False


# --------------------------------------------------------------------------
# The semicolon candidates, the chosen form, and the message-window trace.
# --------------------------------------------------------------------------

def test_candidate_texts_strip_the_semicolon_for_non_text_areas():
    '''A trailing ';' is offered stripped first (that is what OpenGEODE stores),
    with the verbatim proposal as the alternative.'''
    assert osf._candidate_texts("x := 1;", "task") == ["x := 1", "x := 1;"]
    assert osf._candidate_texts("x := 1;  ", "output") == ["x := 1", "x := 1;"]
    # No semicolon: nothing to strip.
    assert osf._candidate_texts("x := 1", "task") == ["x := 1"]
    # A text area keeps its own semicolons.
    assert osf._candidate_texts("dcl x MyInt;", "text_area") == ["dcl x MyInt;"]
    # An empty body after stripping is not offered.
    assert osf._candidate_texts(";", "task") == [";"]


def test_the_user_may_keep_the_verbatim_form(qapp, tmp_path, monkeypatch):
    '''When the proposal has two forms, the review dialog lets the user pick;
    the verbatim form (with the ';') can be applied if they want it.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)
    review_cls = osf._ReviewDialog

    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd): super().__init__()
        def moveToThread(self, t): pass
        def run(self): self.done.emit(("```\nx := 1;\n```", None))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    try:
        # A text_area accepts the semicolon form, so the chosen (only) form is
        # applied verbatim.
        review_cls.pick = 0
        area = _FakeSymbol("dcl x MyInt", construct="text_area")
        assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "m.pr")), area,
                                   ["bad"]) is True
        assert str(area.text) == "x := 1;"
        assert review_cls.last_candidates == ["x := 1;"]
        # For a task the two forms are offered, stripped first; picking the
        # verbatim one ('x := 1;') is tried first, the parser rejects it, and
        # the other form rescues the fix — the user's choice leads, the result
        # still parses.
        review_cls.pick = 1
        task = _FakeSymbol("x := ;")
        assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "m.pr")), task,
                                   ["bad"]) is True
        assert review_cls.last_candidates == ["x := 1", "x := 1;"]
        assert str(task.text) == "x := 1"
    finally:
        review_cls.pick = 0


def test_outcome_is_logged_in_the_message_window(qapp, tmp_path, monkeypatch):
    '''Whatever happens, a line lands in the model's message window, so the user
    can see that orbit was asked and what came back.'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd): super().__init__()
        def moveToThread(self, t): pass
        def run(self): self.done.emit(("```\nx := 1;\n```", None))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    symbol = _FakeSymbol("x := ;")
    assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "m.pr")), symbol,
                               ["bad"]) is True
    lines = symbol.scene().messages_window.lines
    assert any('[Auto fix]' in ln and 'applied' in ln for ln in lines)


def test_a_bad_outcome_is_logged_too(qapp, tmp_path, monkeypatch):
    '''A rollback is logged as well — the user sees the attempt failed and why,
    instead of "nothing happened".'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    from PySide6.QtCore import QObject, Signal
    class _InstantAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd): super().__init__()
        def moveToThread(self, t): pass
        def run(self): self.done.emit(("```\nstill broken ;\n```", None))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _InstantAsker)

    symbol = _FakeSymbol("x := ;", scene=_FakeScene(force_errors=["nope"]))
    assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "m.pr")), symbol,
                               ["bad"]) is False
    lines = symbol.scene().messages_window.lines
    assert any('[Auto fix]' in ln and 'unchanged' in ln for ln in lines)


def test_an_orbit_error_is_logged(qapp, tmp_path, monkeypatch):
    '''If orbit cannot answer, the reason is logged (and a warning shown).'''
    monkeypatch.setenv('ORBIT_ACP_AGENT', FAKE)
    _stub_dialogs(monkeypatch, accept=True)

    from PySide6.QtCore import QObject, Signal
    class _ErrAsker(QObject):
        done = Signal(object)
        def __init__(self, q, cwd): super().__init__()
        def moveToThread(self, t): pass
        def run(self): self.done.emit((None, "no orbit agent"))
        def cancel(self): pass
    monkeypatch.setattr(osf, '_OrbitAsker', _ErrAsker)

    symbol = _FakeSymbol("x := ;")
    assert osf.auto_fix_symbol(_FakeView(str(tmp_path / "m.pr")), symbol,
                               ["bad"]) is False
    assert str(symbol.text) == "x := ;"
    lines = symbol.scene().messages_window.lines
    assert any('[Auto fix]' in ln and 'no orbit agent' in ln for ln in lines)
