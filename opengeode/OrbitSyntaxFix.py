#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Ask orbit to repair the text of a symbol that failed its syntax check.

When the user leaves an editable text box, OpenGEODE parses the text and, on a
syntax error, pops up a warning (see ``SDL_Scene.check_syntax`` in
``opengeode.py``). This module adds, to that pop-up, an **Auto fix** button that
hands the broken text and the parser's complaint to orbit (the same AI agent the
chat panel talks to, with the same bundled SDL skill) and offers the user the
corrected text in a review dialog. Nothing is changed unless the user accepts.

Design constraints this module follows:

* **Self-contained.** All the orbit-facing code lives here, so the editor's own
  modules barely grow: ``opengeode.py`` only adds the button to its pop-up and
  calls :func:`auto_fix_symbol`.
* **Silent when orbit is absent.** If ``orbit_acp`` is not importable, or no
  ``orbit`` agent can be started, :func:`auto_fix_available` is ``False`` and the
  caller must not show any of this UI.
* **Works for every text symbol.** It is driven by what a symbol already offers:
  its ``common_name`` (the parser construct), the text in its editable box
  (``str(symbol.text)``) and the parser's error strings. No per-symbol code.
* **Reuses the chat panel's skill plumbing** (``SKILL_NAME`` / ``SKILL_FILENAME``
  and the resource reader), so orbit gets exactly the SDL construction skill the
  chatbot already stages.

Threading: orbit is asked on a worker thread while a modal progress dialog keeps
the GUI responsive; the review and apply happen back on the GUI thread. The
synchronous ``Conversation.ask`` must never run in the GUI thread.
'''

import os

from PySide6.QtCore import QEventLoop, QObject, QThread, Qt, Signal, Slot
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLabel,
                               QPlainTextEdit, QProgressDialog, QVBoxLayout,
                               QHBoxLayout, QMessageBox)

from .OrbitChatPanel import (SKILL_FILENAME, SKILL_NAME, SKILL_RESOURCE,
                             _read_skill_text, _skill_body, orbit_acp_available)

__all__ = ["auto_fix_available", "auto_fix_symbol"]

#: How long to wait for orbit's answer before giving up (seconds). A text
#: correction is a small task; a longer wait means orbit is stuck.
ASK_TIMEOUT = 180.0

#: How many times orbit is asked in one auto-fix session. The parser usually
#: reports only the FIRST error, so a correction can reveal the next one; the
#: retries let orbit fix them in turn. Each retry keeps whatever the previous
#: one achieved (the user asked for the change to stick). Kept generous because
#: a snippet can hold several errors, but the loop also stops early when orbit
#: starts repeating itself (see _stall_key), so a stuck agent cannot burn the
#: whole budget.
MAX_ATTEMPTS = 6

#: Live worker threads, held so Qt never destroys a QThread that is still
#: running (which aborts the process). Entries drop themselves when done.
_LIVE = set()


def auto_fix_available() -> bool:
    '''True when orbit can be asked to fix a syntax error: the ``orbit_acp``
    library is importable *and* an orbit agent is reachable. The caller shows no
    auto-fix UI unless this is True.'''
    try:
        return bool(orbit_acp_available())
    except Exception:
        # A broken/partial install must never prevent editing the model.
        return False


# ---------------------------------------------------------------------------
# The worker: one question to orbit, off the GUI thread
# ---------------------------------------------------------------------------

class _OrbitAsker(QObject):
    '''Runs one :class:`orbit_acp.Conversation` question on a worker thread.

    It creates the conversation, stages the bundled SDL skill for the next
    question (exactly as the chat panel does), asks, and reports the answer text
    — or the error — through the :attr:`done` signal, which Qt delivers on the
    receiver's thread. The conversation is always closed.
    '''

    #: (answer_text: str | None, error_message: str | None)
    done = Signal(object)

    def __init__(self, question, cwd):
        super().__init__()
        self._question = question
        self._cwd = cwd
        self._chat = None

    @Slot()
    def run(self):
        text = None
        error = None
        try:
            from orbit_acp import Conversation, deny_all
            chat = Conversation(cwd=self._cwd, briefing="", permissions=deny_all,
                                timeout=ASK_TIMEOUT)
            self._chat = chat
            # Stage the same skill the chat panel hands orbit (its own text:
            # orbit loads the body under the name and looks nothing up).
            skill_text = _skill_body(_read_skill_text(SKILL_RESOURCE,
                                                      SKILL_FILENAME))
            if skill_text:
                try:
                    chat.use_skill(SKILL_NAME, skill_text)
                except Exception:
                    # A skill that will not load must not block the question.
                    pass
            text = chat.ask(self._question, timeout=ASK_TIMEOUT)
        except Exception as exc:                      # noqa: BLE001 - report all
            error = str(exc) or exc.__class__.__name__
        finally:
            try:
                if self._chat is not None:
                    self._chat.close()
            except Exception:
                pass
        self.done.emit((text, error))

    def cancel(self) -> None:
        '''Ask orbit to stop the question (best effort).'''
        try:
            if self._chat is not None:
                self._chat.cancel()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Prompt construction and answer extraction
# ---------------------------------------------------------------------------

def _build_question(construct, text, errors):
    '''The prompt handed to orbit: the parser construct, the broken text and
    the parser's complaints, with an explicit, machine-parseable reply format.

    It is deliberately self-contained and forbids tool use. Without that, an
    agent given a working directory full of files explores it (reading, grepping,
    searching for the model and the error) instead of simply rewriting the
    snippet — it then burns the whole timeout on thoughts and tool calls and
    answers nothing, which looks like "orbit did nothing". A syntax fix is a
    pure text rewrite; saying so keeps the answer fast and usable.'''
    problem = "\n".join(str(e) for e in errors) if errors else "(no detail given)"
    return (
        "Rewrite ONE snippet of SDL (ITU-T Z.100) so that it parses. This is a "
        "pure text rewrite.\n"
        "IMPORTANT: answer immediately. Do NOT read files, run commands, search "
        "the project, or use any tool. Everything you need is below.\n\n"
        f"The snippet is the whole body of a '{construct}' symbol in an SDL "
        "model. The editor keeps only the body; it adds the statement "
        "terminator itself. The current snippet does not parse:\n"
        "```\n" + text + "\n```\n\n"
        "The OpenGEODE parser reports:\n" + problem + "\n\n"
        "Give the corrected snippet, keeping its intent and fixing the syntax. "
        "Reply with ONLY the corrected snippet in a single fenced code block "
        "and nothing else. Do not end it with a semicolon."
    )


def _build_retry_question(construct, text, errors, attempt, total):
    '''The prompt for a retry, after a previous correction revealed more errors.

    A parser usually reports only the first error, so fixing it can uncover the
    next one. On a retry orbit is handed the text it just produced and the NEW
    complaints, and is warned to change nothing that already works.'''
    problem = "\n".join(str(e) for e in errors) if errors else "(no detail given)"
    return (
        f"An earlier correction of a '{construct}' snippet in an SDL "
        f"(ITU-T Z.100) model still does not parse (attempt {attempt} of "
        f"{total}). This is a pure text rewrite.\n"
        "IMPORTANT: answer immediately. Do NOT read files, run commands, search "
        "the project, or use any tool. Everything you need is below.\n\n"
        f"The current snippet is:\n```\n" + text + "\n```\n\n"
        "The OpenGEODE parser now reports:\n" + problem + "\n\n"
        "Fix ONLY what is needed to clear these errors and keep everything that "
        "is already correct. Reply with ONLY the corrected snippet in a single "
        "fenced code block and nothing else. Do not end it with a semicolon."
    )


def _extract_code(answer):
    '''Take the corrected snippet out of orbit's answer: the body of the first
    fenced code block, or the whole answer (trimmed) when there is no fence.'''
    if not answer:
        return ""
    fence = "```"
    if fence in answer:
        # Everything after the first fence, up to the next one.
        first = answer.find(fence)
        rest = answer[first + len(fence):]
        # Drop an optional language tag on the same line as the opening fence.
        newline = rest.find("\n")
        body_start = newline + 1 if newline != -1 else 0
        after = rest[body_start:]
        end = after.find(fence)
        snippet = after[:end] if end != -1 else after
        return snippet.strip("\n").rstrip()
    return answer.strip()


def _candidate_texts(proposed, construct):
    '''The forms of orbit's proposal that are worth trying, best first.

    orbit answers with a complete SDL statement, very often WITH the trailing
    ';'. OpenGEODE stores only the body: it adds the ';' itself when it
    generates the model, and check_syntax rejects a text that already ends with
    one ("Remove the semi-colon at the end of the text."). That is true for
    every symbol except a text area (a block of declarations), which does take
    its own semicolons.

    So for anything but a text area whose proposal ends in ';', the form
    OpenGEODE can store is the proposal WITHOUT that final semicolon, and it is
    offered first (the likely-correct default); the verbatim proposal follows as
    the alternative. The parser decides which one is right when applied.'''
    stripped = proposed.rstrip()
    if construct != 'text_area' and stripped.endswith(';'):
        without = stripped[:-1].rstrip()
        if without and without != stripped:
            return [without, stripped]
    return [proposed]


def _stall_key(text, errors):
    '''A fingerprint of a (text, errors) state, used to notice that a retry made
    no progress: if orbit returns the same text AND the parser still reports the
    same errors, asking again will not help, so the loop stops early instead of
    burning every attempt.'''
    return (text.strip(), tuple(str(e).strip() for e in errors))


def _log(view, symbol, message):
    '''Append a line to the model's message window (where OpenGEODE reports
    parse/check results), so an auto-fix always leaves a trace of what it did,
    even when the proposal is rejected. Never raises.'''
    try:
        window = getattr(symbol.scene(), 'messages_window', None)
    except Exception:
        window = None
    if window is None:
        window = getattr(view, 'messages_window', None)
    try:
        if window is not None:
            window.addItem(message)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# The review dialog: current vs proposed, apply or cancel
# ---------------------------------------------------------------------------

class _ReviewDialog(QDialog):
    '''Shows the broken text and orbit's proposed correction side by side and
    lets the user apply or discard it. Applying is the only way text changes.

    When the proposal has a semicolon-tolerant variant (see _candidate_texts),
    a small choice lets the user pick which form to apply — so the review makes
    the actual change visible instead of silently trying forms. The chosen form
    is in :attr:`chosen_text`.
    '''

    def __init__(self, parent, construct, current, proposed, candidates, errors,
                 attempt=1, total=1):
        super().__init__(parent)
        self.setWindowTitle("OpenGEODE - Suggested fix (orbit)")
        self.setModal(True)
        self._candidates = list(candidates)
        self.chosen_text = self._candidates[0] if self._candidates else proposed
        layout = QVBoxLayout(self)

        headline = QLabel(
            f"orbit proposes this correction for the '{construct}' symbol"
            + (f" (attempt {attempt} of {total})" if total > 1 else "")
            + ". Apply it to replace the text?")
        headline.setWordWrap(True)
        layout.addWidget(headline)

        panes = QHBoxLayout()
        for title, value in (("Current (broken)", current),
                             ("Proposed (orbit)", proposed)):
            box = QVBoxLayout()
            box.addWidget(QLabel(title))
            edit = QPlainTextEdit(value)
            edit.setReadOnly(True)
            edit.setMinimumWidth(320)
            box.addWidget(edit)
            panes.addLayout(box)
        layout.addLayout(panes)

        if len(self._candidates) > 1:
            # The proposal differs only by a trailing ';' OpenGEODE does not
            # want inside a symbol. Let the user choose; the default is the
            # form that will parse.
            row = QHBoxLayout()
            row.addWidget(QLabel("Apply:"))
            self._choice = QComboBox()
            for cand in self._candidates:
                label = repr(cand) if '\n' not in cand else cand.replace('\n', ' ⏎ ')
                self._choice.addItem(label, cand)
            self._choice.currentIndexChanged.connect(self._on_choice)
            row.addWidget(self._choice, 1)
            layout.addLayout(row)

        if errors:
            why = QLabel("Parser error: " + " ".join(str(e) for e in errors))
            why.setWordWrap(True)
            layout.addWidget(why)

        buttons = QDialogButtonBox()
        self._apply = buttons.addButton("Apply", QDialogButtonBox.AcceptRole)
        buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._apply.setDefault(True)

    def _on_choice(self, index):
        if 0 <= index < len(self._candidates):
            self.chosen_text = self._candidates[index]


# ---------------------------------------------------------------------------
# The public entry point called by the editor's syntax-error pop-up
# ---------------------------------------------------------------------------

def _set_symbol_text(symbol, value):
    '''Replace the symbol's text and let it re-lay out.'''
    symbol.text.setPlainText(value)
    try:
        symbol.text.try_resize()
    except AttributeError:
        pass


def _syntax_errors(scene, symbol):
    '''The parser's complaints for the symbol's current text (empty when it
    parses, or when there is no scene to ask).'''
    try:
        return list(scene.syntax_errors(symbol)) if scene is not None else []
    except Exception:
        return []


def _ask_orbit(view, question, model_dir):
    '''Run one question to orbit on a worker thread, under a modal progress
    dialog. Returns ``(status, payload)`` where status is ``'ok'`` (payload is
    orbit's raw answer), ``'cancelled'`` or ``'error'`` (payload is the message).

    Kept as a function so each retry is one clean ask: the threading dance and
    the progress dialog are identical every time.'''
    progress = QProgressDialog("Asking orbit to fix the syntax error…",
                               "Cancel", 0, 0, view)
    progress.setWindowTitle("OpenGEODE - Auto fix")
    progress.setWindowModality(Qt.ApplicationModal)
    progress.setMinimumDuration(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    progress.show()

    loop = QEventLoop()
    thread = QThread()
    asker = _OrbitAsker(question, model_dir)
    asker.moveToThread(thread)
    result = {}

    def _on_done(payload):
        answer, error = payload
        result["answer"] = answer
        result["error"] = error
        loop.quit()

    thread.started.connect(asker.run)
    asker.done.connect(_on_done)
    # Stop the worker thread once the answer is in (or the box was cancelled).
    asker.done.connect(thread.quit)
    progress.canceled.connect(loop.quit)
    # Keep the worker objects alive until the thread really stops: a QThread
    # destroyed while running aborts the process. _LIVE holds them; the entry
    # is dropped (and the objects deleted) when the thread finishes.
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(asker.deleteLater)
    _LIVE.add(thread)
    thread.finished.connect(lambda: _LIVE.discard(thread))
    thread.start()
    # NOTE: QProgressDialog.close() makes wasCanceled() report True, so the
    # state must be read BEFORE closing it — reading it afterwards would make
    # every run look cancelled and the fix would never be applied.
    cancelled = False
    try:
        loop.exec()
    finally:
        cancelled = progress.wasCanceled()
        if cancelled:
            asker.cancel()
        progress.close()
        thread.quit()
        thread.wait(5000)

    if cancelled:
        return 'cancelled', None
    if result.get("error"):
        return 'error', result.get("error")
    return 'ok', result.get("answer")


def auto_fix_symbol(view, symbol, errors, max_attempts=MAX_ATTEMPTS) -> bool:
    '''Ask orbit to fix ``symbol``'s syntax error and let the user apply the
    result, retrying a few times when a correction is not enough on its own.

    A parser normally reports only the FIRST error, so a correction can reveal
    the next one; up to ``max_attempts`` rounds are run, each handing orbit the
    text it just produced plus the NEW complaints. The loop stops early if orbit
    repeats the same text with the same errors (no progress). Every accepted
    correction is kept — a retry never reverts the user's change.

    Returns True when the symbol finally parses (the caller should then let the
    normal post-edit path run, recording the change as one undo step); False
    when it does not — nothing was applied, the user declined, orbit failed, or
    the attempts ran out (in which case the last accepted text is still kept, so
    the user does not lose the work done so far).

    All UI lives here; the caller only inspects the return value.
    '''
    text = str(getattr(symbol, "text", "") or "")
    if not text.strip():
        return False
    construct = getattr(symbol, "common_name", "") or "symbol"
    model_dir = _model_dir(view)
    scene = symbol.scene()

    current = text                 # the running, accepted text
    current_errors = list(errors)  # its current complaints
    seen = {_stall_key(current, current_errors)}
    stalled = False
    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            question = _build_question(construct, current, current_errors)
        else:
            question = _build_retry_question(construct, current, current_errors,
                                             attempt, max_attempts)

        status, payload = _ask_orbit(view, question, model_dir)
        if status == 'cancelled':
            _log(view, symbol, "[Auto fix] cancelled while orbit was answering.")
            return False
        if status == 'error':
            _log(view, symbol, "[Auto fix] orbit could not answer: " + str(payload))
            QMessageBox.warning(
                view, "OpenGEODE - Auto fix",
                "orbit could not answer:\n" + str(payload) +
                "\n\nPlease fix the syntax error manually.")
            return False

        proposed = _extract_code(payload)
        if not proposed.strip():
            _log(view, symbol, "[Auto fix] orbit returned no usable correction "
                 "(raw answer: " + repr(payload)[:300] + ")")
            if attempt == 1:
                QMessageBox.warning(
                    view, "OpenGEODE - Auto fix",
                    "orbit returned no usable correction.\n"
                    "Please fix the syntax error manually.")
            return False

        # The forms of the proposal worth trying (orbit usually adds the ';'
        # that OpenGEODE wants kept out of a symbol's text — see
        # _candidate_texts).
        candidates = _candidate_texts(proposed, construct)
        dialog = _ReviewDialog(view, construct, current, proposed, candidates,
                               current_errors, attempt, max_attempts)
        if dialog.exec() != QDialog.Accepted:
            if current != text:
                _log(view, symbol, "[Auto fix] kept the correction from the "
                     "previous attempt at your request; the symbol still has "
                     "syntax errors.")
            else:
                _log(view, symbol, "[Auto fix] proposal discarded by the user "
                     "(orbit proposed: " + proposed.replace("\n", " ") + ")")
            return False

        # Try the user's chosen form first, then any alternative; stop at the
        # first that parses. chosen_errors is the chosen form's outcome, which
        # is what a retry must build on.
        chosen = dialog.chosen_text
        order = [chosen] + [c for c in candidates if c != chosen]
        chosen_errors = []
        applied = None
        for index, candidate in enumerate(order):
            _set_symbol_text(symbol, candidate)
            remaining = _syntax_errors(scene, symbol)
            if index == 0:
                chosen_errors = remaining
            if not remaining:
                applied = candidate
                break

        if applied is not None:
            _log(view, symbol, "[Auto fix] applied orbit's correction"
                 + (f" (attempt {attempt})" if attempt > 1 else "") + ": "
                 + applied.replace("\n", " "))
            return True

        # Not parseable yet: keep the chosen form in the widget and ask orbit
        # again, so a correction that revealed the next error can be completed.
        current = chosen
        current_errors = chosen_errors
        key = _stall_key(current, current_errors)
        if key in seen:
            # The retry produced the very same text with the same errors: no
            # progress, so stop early rather than repeat the same question.
            stalled = True
            _log(view, symbol, "[Auto fix] orbit repeated the same correction; "
                 "stopping early. " + " ".join(str(e) for e in current_errors))
            break
        seen.add(key)
        _log(view, symbol, f"[Auto fix] attempt {attempt}/{max_attempts} still "
             "does not parse; asking orbit again. "
             + " ".join(str(e) for e in chosen_errors))

    # Attempts exhausted (or orbit stopped making progress): keep the last
    # accepted text (the user asked for the change to stick) and let them finish
    # by hand.
    _set_symbol_text(symbol, current)
    remaining = _syntax_errors(scene, symbol)
    reason = ("orbit stopped making progress" if stalled else
              f"orbit could not fix it in {max_attempts} attempts")
    _log(view, symbol, f"[Auto fix] gave up: {reason}; the text was kept as "
         "last proposed and still has syntax errors. "
         + " ".join(str(e) for e in remaining))
    QMessageBox.warning(
        view, "OpenGEODE - Auto fix",
        f"orbit could not fully fix the syntax error ({reason}).\n\n"
        + "\n".join(str(e) for e in remaining) +
        "\n\nThe text was left as orbit last proposed; please finish it by hand.")
    return False


def _model_dir(view) -> str:
    '''The directory of the model being edited — orbit's working directory.
    Falls back to the process directory when no file is known.'''
    filename = getattr(view, "filename", "") or ""
    if filename:
        return os.path.dirname(os.path.abspath(filename)) or os.getcwd()
    return os.getcwd()
