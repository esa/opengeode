#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenGEODE - AI Chat panel backed by orbit (via the orbit-acp library)

A right-panel dock tab that opens a conversation with orbit. The conversation
runs on worker threads and reaches the panel through Qt signals, following
the pattern from orbit-acp's GUI integration guide. A permission request opens
a dialog and the worker waits for the click; the Stop button cancels the
running question.

If the ``orbit_acp`` Python package is not importable, or if no ``orbit``
binary is on the PATH (and ``ORBIT_ACP_AGENT`` is unset), the panel stays
visible but disabled with a short explanatory message, so OpenGEODE itself is
unaffected.

Copyright (c) 2012-2026 Maxime Perrotin & European Space Agency
"""
from __future__ import annotations

import os
import threading

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)

__all__ = ["OrbitChatPanel", "orbit_acp_available"]

# The orbit_acp import is wrapped so OpenGEODE never fails to start when the
# library (or orbit itself) is absent. Everything below guards on these.
try:
    import orbit_acp
    from orbit_acp import Conversation, OrbitError, REJECT
    _ORBIT_ACP_IMPORTABLE = True
except ImportError:
    orbit_acp = None
    Conversation = None
    OrbitError = None
    REJECT = "reject"
    _ORBIT_ACP_IMPORTABLE = False


def orbit_acp_available() -> bool:
    """True when the orbit_acp library is importable *and* an orbit agent can
    be started on this machine. Cheap to call; used by the panel to decide
    whether to enable itself."""
    if not _ORBIT_ACP_IMPORTABLE:
        return False
    try:
        return bool(orbit_acp.available())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# The SDL context briefing sent ahead of the first question. It tells orbit
# what kind of model it is editing and which files matter, so it can modify
# the .pr (and the ASN.1 dataview) to create model artefacts.
# ---------------------------------------------------------------------------
def _sdl_briefing(pr_file: str, asn1_file: str) -> str:
    """Build the one-shot briefing that goes ahead of the first question.

    Tells the agent it is working inside the OpenGEODE SDL editor, points it
    at the current .pr model file (and the ASN.1 dataview when there is one),
    and explains the convention that editing the file on disk will be picked
    up by the editor's external-modification monitor and offered for reload.
    """
    parts = [
        "You are working inside OpenGEODE, a graphical editor for SDL "
        "(Specification and Description Language, ITU-T Z.100) state "
        "machines used by the TASTE toolchain.",
        "",
        "The current SDL model is a .pr file. You may edit it on disk to "
        "create or modify model artefacts (states, transitions, inputs, "
        "outputs, tasks, procedures, etc.). OpenGEODE watches the file and "
        "will offer to reload it from disk when you are done, so your "
        "changes appear in the diagram.",
    ]
    if pr_file:
        parts.append(f"\nThe current model file is: {pr_file}")
    if asn1_file:
        parts.append(
            f"The ASN.1 dataview file is: {asn1_file}\n"
            "You may also edit the ASN.1 file to add or change the data "
            "types used by the SDL model."
        )
    else:
        parts.append(
            "There is no ASN.1 dataview associated with this model yet; "
            "you may create one and reference it from the .pr file with a "
            "USE clause if the model needs user-defined types."
        )
    parts.append(
        "\nWhen you need to run a command or edit a file, ask for "
        "permission: the person using the editor will approve it."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# The agent bridge: a QObject that owns the Conversation and drives it from
# worker threads, forwarding every event (and every permission request) to
# the GUI thread through signals. This is the pattern from orbit-acp's
# GUI integration guide (examples/qt_chat.py).
# ---------------------------------------------------------------------------
class OrbitAgent(QObject):
    """The conversation, driven from the GUI thread with the blocking done
    on threads of its own.

    Signals are emitted from worker threads and queued to the GUI thread
    because the receiver (the panel) is a QObject living there.
    """

    event = Signal(object)        # every event of the running question
    permission = Signal(object)   # a PermissionRequest to answer with answer()
    turn_done = Signal(str)        # why the question stopped
    failed = Signal(str)           # a setup or runtime error, as text
    ready = Signal()              # the conversation is open and usable

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat = None
        self._answer = REJECT
        self._answered = threading.Event()
        # A files handler the panel can set so orbit reads/writes through
        # the editor's buffers when the app holds files. None disables it.
        self._files = None
        # Hook called (on the GUI thread) after a turn ends; used by the
        # panel to nudge the editor to reload after orbit edited the model.
        self.on_turn_done = None

    # -- setup ---------------------------------------------------------------
    def start(self, cwd, briefing=""):
        """Open the conversation on a worker thread (starting orbit takes a
        moment). Emits ``ready`` when it is usable, or ``failed``."""
        def work():
            try:
                self.chat = Conversation(
                    cwd=cwd, briefing=briefing,
                    permissions=self._rule,
                    files=self._files,
                )
            except OrbitError as exc:
                self.failed.emit(str(exc))
                return
            except Exception as exc:  # pragma: no cover - defensive
                self.failed.emit(f"{type(exc).__name__}: {exc}")
                return
            self.ready.emit()
        threading.Thread(target=work, daemon=True).start()

    # -- asking --------------------------------------------------------------
    def ask(self, question):
        """Start a worker that iterates ``stream`` and forwards each event.
        Emits ``turn_done`` when the question stops."""
        def work():
            reason = "error"
            try:
                for ev in self.chat.stream(question):
                    self.event.emit(ev)
                reason = self.chat.stopped_because
            except OrbitError as exc:
                self.failed.emit(str(exc))
            except Exception as exc:  # pragma: no cover - defensive
                self.failed.emit(f"{type(exc).__name__}: {exc}")
            finally:
                self.turn_done.emit(reason)
        threading.Thread(target=work, daemon=True).start()

    def cancel(self):
        """Stop the running question and wake a permission dialog that is
        waiting for a click. Safe from the GUI thread."""
        if self.chat is not None:
            try:
                self.chat.cancel()
            except Exception:
                pass
        self.answer(REJECT)

    # -- permissions (run on the worker) ------------------------------------
    def _rule(self, req):
        self._answered.clear()
        self._answer = REJECT
        self.permission.emit(req)   # the panel opens a dialog
        self._answered.wait()
        return self._answer

    def answer(self, option):
        """Called from the dialog, on the GUI thread, to resolve a pending
        permission request."""
        self._answer = option
        self._answered.set()

    # -- teardown -----------------------------------------------------------
    def stop(self):
        """Close the conversation on a worker so the window does not freeze
        for the process to end."""
        chat, self.chat = self.chat, None
        if chat is not None:
            threading.Thread(target=chat.close, daemon=True).start()


# ---------------------------------------------------------------------------
# The panel itself: a chat view, an input line and a Stop button. It owns an
# OrbitAgent and connects its signals to its own slots (which run on the GUI
# thread). The panel is given a reference to the OG_MainWindow so it can read
# the current model file path and the ASN.1 file path, and so it can trigger
# a reload when orbit has edited the model on disk.
# ---------------------------------------------------------------------------
class OrbitChatPanel(QWidget):
    """A chat panel that talks to orbit about the SDL model open in the
    editor. Degrades to a disabled, informative placeholder when orbit_acp
    or orbit is not available."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._busy = False
        self._agent = None

        # --- UI ---
        self.view = QTextEdit(readOnly=True)
        self.view.setPlaceholderText("The orbit chat will appear here.")
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("orbit not available")
        self.entry.setEnabled(False)
        self.entry.returnPressed.connect(self._send)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(self.view)
        bottom = QHBoxLayout()
        bottom.addWidget(self.entry, stretch=1)
        bottom.addWidget(self.stop_btn)
        lay.addLayout(bottom)

        # --- Agent / availability ---
        if not _ORBIT_ACP_IMPORTABLE:
            self._show_unavailable(
                "The orbit-acp library is not installed. "
                "Install it with: python -m pip install -e "
                "/path/to/orbit-acp/python")
            return

        if not orbit_acp_available():
            self._show_unavailable(
                "orbit was not found on the PATH. Install orbit from its "
                "checkout (python -m pip install -e .) or set the "
                "ORBIT_ACP_AGENT environment variable to the agent to run.")
            return

        # orbit_acp is importable and orbit is available: wire up the agent.
        self._agent = OrbitAgent(self)
        self._agent.ready.connect(self._on_ready)
        self._agent.event.connect(self._on_event)
        self._agent.permission.connect(self._on_permission)
        self._agent.turn_done.connect(self._on_turn_done)
        self._agent.failed.connect(self._on_failed)
        self._start_conversation()

    # -- layout helpers ------------------------------------------------------
    def _show_unavailable(self, message):
        """Disable the panel and show a short explanation instead of a chat."""
        self.view.setHtml(f"<i>{message}</i>")
        self.entry.setPlaceholderText("orbit not available")
        self.entry.setEnabled(False)
        self.stop_btn.setEnabled(False)

    # -- context for the conversation ---------------------------------------
    def _model_dir(self) -> str:
        """The working directory for the conversation: the directory of the
        current .pr model, falling back to the current directory."""
        view = getattr(self.main_window, "view", None)
        pr = getattr(view, "filename", "") or ""
        if pr:
            return os.path.dirname(os.path.abspath(pr)) or os.getcwd()
        return os.getcwd()

    def _pr_file(self) -> str:
        view = getattr(self.main_window, "view", None)
        return getattr(view, "filename", "") or ""

    def _asn1_file(self) -> str:
        return getattr(self.main_window, "current_asn1_file", None) or ""

    def _briefing(self) -> str:
        return _sdl_briefing(self._pr_file(), self._asn1_file())

    def _start_conversation(self):
        """Open the conversation, with the model directory as cwd and a
        briefing that tells orbit about the SDL model."""
        self.view.setHtml("<i>Starting orbit…</i>")
        self.entry.setPlaceholderText("Ask orbit… (starting)")
        self._agent.start(self._model_dir(), briefing=self._briefing())

    # -- agent signal slots (run on the GUI thread) -------------------------
    @Slot()
    def _on_ready(self):
        self.view.clear()
        self.entry.setPlaceholderText("Ask orbit about the SDL model…")
        self.entry.setEnabled(True)
        self.entry.setFocus()
        self.view.append(
            "<i>Connected to orbit. The current model is "
            f"{self._pr_file() or 'unsaved'}.</i>")

    @Slot(object)
    def _on_event(self, ev):
        kind = getattr(ev, "kind", "")
        if kind == "text":
            cursor = self.view.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(ev.text)
            self.view.setTextCursor(cursor)
        elif kind == "thought":
            cursor = self.view.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(f"\n[thinking] {ev.text}")
            self.view.setTextCursor(cursor)
        elif kind == "tool":
            status = getattr(ev, "status", "")
            title = getattr(ev, "title", "")
            # When an edit tool finishes, note the files it touched so the
            # user knows a reload may be needed.
            extra = ""
            files = getattr(ev, "files", None) or []
            if getattr(ev, "done", False) and files:
                extra = " → " + ", ".join(files)
            self.view.append(f"<i>[{title}: {status}{extra}]</i>")
        elif kind == "plan":
            steps = getattr(ev, "steps", None) or []
            if steps:
                self.view.append("<i>Plan:</i>")
                for step in steps:
                    mark = {"pending": "○", "in_progress": "◐",
                            "completed": "●"}.get(getattr(step, "status", ""),
                                                  "•")
                    self.view.append(f"<i>  {mark} {step.title}</i>")
        elif kind == "usage":
            used = getattr(ev, "used", 0)
            size = getattr(ev, "size", 0)
            if size:
                self.view.append(f"<i>[context: {used}/{size} tokens]</i>")
        elif kind == "task":
            title = getattr(ev, "title", "")
            status = getattr(ev, "status", "")
            if title:
                self.view.append(f"<i>⟡ {title}: {status}</i>")

    @Slot(object)
    def _on_permission(self, req):
        """Open a dialog asking whether to allow what orbit wants to do.
        The worker is waiting on _answered; the click resolves it."""
        title = getattr(req, "title", "Allow?")
        command = getattr(req, "command", "")
        text = title
        if command:
            text += f"\n\n{command}"
        box = QMessageBox(self)
        box.setWindowTitle("orbit asks permission")
        box.setIcon(QMessageBox.Question)
        box.setText(text)
        btn_once = box.addButton("Allow once", QMessageBox.AcceptRole)
        btn_always = box.addButton("Allow always", QMessageBox.AcceptRole)
        box.addButton("Reject", QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is btn_once:
            self._agent.answer("once")
        elif clicked is btn_always:
            self._agent.answer("always")
        else:
            self._agent.answer(REJECT)

    @Slot(str)
    def _on_turn_done(self, reason):
        self._busy = False
        if reason and reason != "done":
            self.view.append(f"<i>({reason})</i>")
        self.entry.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.entry.setFocus()
        # Nudge the editor to check for external modifications: if orbit
        # edited the .pr or ASN.1 file on disk, the existing file monitor
        # will offer to reload. This makes the model artefacts appear.
        self._maybe_check_modifications()

    @Slot(str)
    def _on_failed(self, message):
        self._busy = False
        self.view.append(f"<i>error: {message}</i>")
        self.entry.setEnabled(self._agent is not None and self._agent.chat is not None)
        self.stop_btn.setEnabled(False)

    # -- user actions -------------------------------------------------------
    def _send(self):
        if self._agent is None:
            return
        question = self.entry.text().strip()
        if not question or self._busy:
            return
        self.entry.clear()
        self.entry.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._busy = True
        self.view.append(f"<b>you:</b> {question}")
        self.view.append("<b>orbit:</b> ")
        self._agent.ask(question)

    def _stop(self):
        if self._agent is not None:
            self._agent.cancel()

    def _maybe_check_modifications(self):
        """Ask the main window to check whether orbit edited the model on
        disk. The main window's ``check_external_modifications`` shows the
        reload dialog when a tracked file changed."""
        mw = self.main_window
        check = getattr(mw, "check_external_modifications", None)
        if callable(check):
            try:
                check()
            except Exception:
                pass

    # -- shutdown -----------------------------------------------------------
    def closeEvent(self, event):
        if self._agent is not None:
            self._agent.stop()
        super().closeEvent(event)

    def _agent_stop_on_close(self):
        """Called by the main window on close: stop the conversation on a
        worker thread so the window does not wait for the orbit process."""
        if self._agent is not None:
            self._agent.stop()
