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
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QPlainTextEdit,
                               QProgressDialog, QVBoxLayout, QHBoxLayout,
                               QMessageBox)

from .OrbitChatPanel import (SKILL_FILENAME, SKILL_NAME, SKILL_RESOURCE,
                             _read_skill_text, _skill_body, orbit_acp_available)

__all__ = ["auto_fix_available", "auto_fix_symbol"]

#: How long to wait for orbit's answer before giving up (seconds). A text
#: correction is a small task; a longer wait means orbit is stuck.
ASK_TIMEOUT = 180.0

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
    the parser's complaints, with an explicit, machine-parseable reply format.'''
    problem = "\n".join(errors) if errors else "(no detail given)"
    return (
        "You are helping repair one symbol in an SDL (ITU-T Z.100) model "
        "inside the OpenGEODE editor.\n"
        f"The symbol is a '{construct}' construct that failed to parse.\n\n"
        "The current (broken) text inside the symbol is:\n"
        "```\n" + text + "\n```\n\n"
        "The parser reported:\n" + problem + "\n\n"
        "Give the corrected text for that symbol only. Keep the same intent, "
        "fix the syntax, and do not add other symbols. Reply with ONLY the "
        "corrected text in a single fenced code block, with no explanation and "
        "no surrounding text."
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


# ---------------------------------------------------------------------------
# The review dialog: current vs proposed, apply or cancel
# ---------------------------------------------------------------------------

class _ReviewDialog(QDialog):
    '''Shows the broken text and orbit's proposed correction side by side and
    lets the user apply or discard it. Applying is the only way text changes.'''

    def __init__(self, parent, construct, current, proposed, errors):
        super().__init__(parent)
        self.setWindowTitle("OpenGEODE - Suggested fix (orbit)")
        self.setModal(True)
        layout = QVBoxLayout(self)

        headline = QLabel(
            f"orbit proposes this correction for the '{construct}' symbol. "
            "Apply it to replace the text?")
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

        if errors:
            why = QLabel("Parser error: " + " ".join(errors))
            why.setWordWrap(True)
            layout.addWidget(why)

        buttons = QDialogButtonBox()
        self._apply = buttons.addButton("Apply", QDialogButtonBox.AcceptRole)
        buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._apply.setDefault(True)


# ---------------------------------------------------------------------------
# The public entry point called by the editor's syntax-error pop-up
# ---------------------------------------------------------------------------

def auto_fix_symbol(view, symbol, errors) -> bool:
    '''Ask orbit to fix ``symbol``'s syntax error and let the user apply the
    result.

    Returns True when a correction was applied and the symbol now parses (the
    caller should then let the normal post-edit path run, recording the change
    as one undo step); False when nothing was applied — user cancelled, orbit
    unavailable, an error occurred, or the suggestion did not fix the problem.

    All UI lives here; the caller only inspects the return value.
    '''
    text = str(getattr(symbol, "text", "") or "")
    if not text.strip():
        return False
    construct = getattr(symbol, "common_name", "") or "symbol"
    model_dir = _model_dir(view)

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
    asker = _OrbitAsker(_build_question(construct, text, errors), model_dir)
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
    try:
        loop.exec()
    finally:
        if progress.wasCanceled():
            asker.cancel()
        progress.close()
        thread.quit()
        thread.wait(5000)

    if progress.wasCanceled():
        return False
    if result.get("error"):
        QMessageBox.warning(
            view, "OpenGEODE - Auto fix",
            "orbit could not answer:\n" + str(result["error"]) +
            "\n\nPlease fix the syntax error manually.")
        return False

    proposed = _extract_code(result.get("answer"))
    if not proposed.strip():
        QMessageBox.warning(
            view, "OpenGEODE - Auto fix",
            "orbit returned no usable correction.\n"
            "Please fix the syntax error manually.")
        return False

    dialog = _ReviewDialog(view, construct, text, proposed, errors)
    if dialog.exec() != QDialog.Accepted:
        return False

    # Apply the correction, then verify it actually parses. On failure, restore
    # the original text so the model is left exactly as the user had it.
    # syntax_errors lives on the scene (SDL_Scene), not the view.
    scene = symbol.scene()
    symbol.text.setPlainText(proposed)
    try:
        symbol.text.try_resize()
    except AttributeError:
        pass
    remaining = []
    try:
        if scene is not None:
            remaining = scene.syntax_errors(symbol)
    except Exception:
        remaining = []
    if remaining:
        symbol.text.setPlainText(text)
        try:
            symbol.text.try_resize()
        except AttributeError:
            pass
        QMessageBox.warning(
            view, "OpenGEODE - Auto fix",
            "orbit's suggestion still does not parse:\n" +
            "\n".join(remaining) + "\n\nPlease fix the syntax error manually.")
        return False
    return True


def _model_dir(view) -> str:
    '''The directory of the model being edited — orbit's working directory.
    Falls back to the process directory when no file is known.'''
    filename = getattr(view, "filename", "") or ""
    if filename:
        return os.path.dirname(os.path.abspath(filename)) or os.getcwd()
    return os.getcwd()
