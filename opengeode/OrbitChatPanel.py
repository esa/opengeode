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
import shutil
import threading

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)

__all__ = ["OrbitChatPanel", "orbit_acp_available"]

# The name of the SDL model-construction skill bundled with OpenGEODE, as
# declared in the YAML frontmatter of orbit_skills/SDL_SKILL_DOCUMENTATION.md.
# The panel installs this skill into orbit's global skills directory at
# startup so orbit discovers it and advertises it in <available_skills>
# every turn. The briefing tells the model to load it via the skill() tool.
SKILL_NAME = "sdl-model-construction"
SKILL_FILENAME = "SDL_SKILL_DOCUMENTATION.md"

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
# Skill installation: copy the bundled SDL skill into orbit's global skills
# directory so orbit can discover it. Orbit discovers skills from
# ~/.config/orbit/skills/ (global) and <project>/.orbit/skills/
# (per-project). The conversation's cwd is the model's directory, which
# generally has no .orbit/skills/, so the global directory is the
# reliable place.
# ---------------------------------------------------------------------------
def _orbit_global_skills_dir() -> str:
    """The global directory orbit scans for skills, mirroring orbit's own
    config.paths._global_dir() / "skills" logic."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "orbit", "skills")


def _bundled_skill_path() -> str:
    """The path to the SDL skill file bundled alongside the OpenGEODE
    package. Checks several candidate locations so the skill is found
    whether OpenGEODE runs from the source checkout (orbit_skills/ next
    to the opengeode/ package dir) or from an installed wheel (the
    orbit_skills/ directory copied into the package itself)."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        # Source checkout: opengeode/../orbit_skills/
        os.path.join(os.path.dirname(here), "orbit_skills", SKILL_FILENAME),
        # Installed package: opengeode/orbit_skills/
        os.path.join(here, "orbit_skills", SKILL_FILENAME),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]  # default to source-tree path


def _install_skill() -> None:
    """Copy the bundled SDL skill into orbit's global skills directory so
    orbit can discover it by name. Safe to call on every startup: it only
    copies when the destination is missing or out of date. Silently skips
    when the source is absent (e.g. running from a build that did not ship
    the skill)."""
    src = _bundled_skill_path()
    if not os.path.isfile(src):
        return
    dest_dir = _orbit_global_skills_dir()
    dest = os.path.join(dest_dir, SKILL_FILENAME)
    try:
        os.makedirs(dest_dir, exist_ok=True)
        if (not os.path.isfile(dest)
                or os.path.getmtime(src) > os.path.getmtime(dest)):
            shutil.copy2(src, dest)
    except OSError:
        # If we cannot write to the config directory, orbit simply will
        # not discover the skill; the panel still works, just without
        # the SDL guidance loaded. Not worth a user-visible error.
        pass


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
    parts.append(
        f"\nA skill called '{SKILL_NAME}' is available to you. "
        f"It contains the complete syntax and semantic reference for "
        f"creating and modifying SDL models for OpenGEODE. Load it with "
        f"skill(name=\'{SKILL_NAME}\') BEFORE working on any SDL "
        f"model — do not merely mention it. The skill covers grammar, "
        f"semantic rules, ASN.1 integration, CLI, CIF annotations, and "
        f"the agent operating procedure for safe model editing."
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

    # CSS injected into the chat view so rendered markdown (code blocks,
    # headings, lists, tables) has a consistent, readable style.
    _CHAT_CSS = (
        "<style>\n"
        " pre { background-color:#f4f4f4; border:1px solid #ddd;"
        " border-radius:3px; padding:4px; margin:4px 0;"
        " font-family:monospace; white-space:pre-wrap; }\n"
        " code { font-family:monospace; background-color:#f0f0f0;"
        " padding:1px 3px; border-radius:2px; }\n"
        " h1 { font-size:large; margin:8px 0 4px; }\n"
        " h2 { font-size:medium; margin:8px 0 4px; }\n"
        " h3 { font-size:medium; margin:6px 0 2px; }\n"
        " table { border-collapse:collapse; margin:4px 0; }\n"
        " th, td { border:1px solid #ccc; padding:2px 6px; }\n"
        " ul, ol { margin:4px 0; padding-left:20px; }\n"
        " li { margin:2px 0; }\n"
        "</style>"
    )

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._busy = False
        self._agent = None

        # Conversation rendered as a list of message records. Each record is
        # a dict: {"role": ..., "html": ..., "streaming": bool}. The panel
        # re-renders the whole view as HTML whenever this list changes.
        self._messages = []
        # Accumulated raw markdown text for the assistant reply currently
        # streaming in.  Cleared when the turn finishes.
        self._assistant_text = ""

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

    # -- markdown helpers ---------------------------------------------------
    @staticmethod
    def _md_to_html(md: str) -> str:
        """Convert a markdown string to HTML using Qt's built-in parser.

        Qt's ``QTextDocument.setMarkdown`` supports CommonMark plus a few
        GitHub-flavoured extensions (fenced code blocks, tables, strikethrough).
        We render into a throw-away document and read back the HTML body.
        """
        doc = QTextDocument()
        doc.setMarkdown(md)
        html = doc.toHtml()
        # ``toHtml`` returns a full HTML page with a body. Extract just the
        # inner body so we can splice it into our own message structure.
        start = html.find("<body", )
        if start != -1:
            start = html.find(">", start) + 1
            end = html.rfind("</body>")
            if end != -1:
                html = html[start:end]
        return html

    @staticmethod
    def _html_escape(text: str) -> str:
        """Escape plain text for safe inclusion in HTML."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _render_view(self):
        """Rebuild the chat view HTML from ``self._messages``.

        Each message is rendered as a styled block.  Assistant markdown is
        converted to HTML via ``QTextDocument.setMarkdown``; user text and
        tool/plan/task status lines are escaped and shown inline.
        """
        parts = []
        for msg in self._messages:
            role = msg.get("role", "")
            html = msg.get("html", "")
            if not html:
                continue
            if role == "user":
                parts.append(
                    f'<p style="margin:6px 0;">'
                    f'<b style="color:#0066cc;">you:</b> {html}</p>')
            elif role == "assistant":
                parts.append(
                    f'<p style="margin:6px 0;">'
                    f'<b style="color:#006600;">orbit:</b></p>'
                    f'<div style="margin-left:8px;">{html}</div>')
            else:
                # tool events, plan, usage, task, system lines
                parts.append(html)
        self.view.setHtml(self._CHAT_CSS + "\n".join(parts))
        # Scroll to bottom so the latest content is visible.
        sb = self.view.verticalScrollBar()
        sb.setValue(sb.maximum())

    # -- layout helpers ------------------------------------------------------
    def _show_unavailable(self, message):
        """Disable the panel and show a short explanation instead of a chat."""
        self._messages = [
            {"role": "system", "html": f"<i>{self._html_escape(message)}</i>"}
        ]
        self._render_view()
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
        # Install the bundled SDL skill so orbit can discover and load it.
        _install_skill()
        self._messages = [
            {"role": "system", "html": "<i>Starting orbit…</i>"}
        ]
        self._render_view()
        self.entry.setPlaceholderText("Ask orbit… (starting)")
        self._agent.start(self._model_dir(), briefing=self._briefing())

    # -- agent signal slots (run on the GUI thread) -------------------------
    @Slot()
    def _on_ready(self):
        self._messages = []
        self._render_view()
        self.entry.setPlaceholderText("Ask orbit about the SDL model…")
        self.entry.setEnabled(True)
        self.entry.setFocus()
        pr_file = self._pr_file() or 'unsaved'
        self._messages.append({
            "role": "system",
            "html": f"<i>Connected to orbit. The current model is "
                    f"{self._html_escape(pr_file)}.</i>",
        })
        self._render_view()

    @Slot(object)
    def _on_event(self, ev):
        kind = getattr(ev, "kind", "")
        if kind == "text":
            # Accumulate the raw markdown text; show it live as escaped plain
            # text so the user sees streaming output.  The full markdown is
            # rendered when the turn finishes (see _on_turn_done).
            self._assistant_text += ev.text
            html = self._html_escape(self._assistant_text).replace("\n", "<br>")
            if self._messages and self._messages[-1].get("role") == "assistant" \
                    and self._messages[-1].get("streaming"):
                self._messages[-1]["html"] = html
            else:
                self._messages.append(
                    {"role": "assistant", "html": html, "streaming": True})
            self._render_view()
        elif kind == "thought":
            html = (f"<p style='margin:4px 0;color:#888;'><i>[thinking] "
                    f"{self._html_escape(ev.text)}</i></p>")
            self._messages.append({"role": "thought", "html": html})
            self._render_view()
        elif kind == "tool":
            status = getattr(ev, "status", "")
            title = getattr(ev, "title", "")
            # When an edit tool finishes, note the files it touched so the
            # user knows a reload may be needed.
            extra = ""
            files = getattr(ev, "files", None) or []
            if getattr(ev, "done", False) and files:
                extra = " → " + ", ".join(files)
            html = (f"<p style='margin:2px 0;color:#555;'><i>["
                    f"{self._html_escape(title)}: {self._html_escape(status)}"
                    f"{self._html_escape(extra)}]</i></p>")
            self._messages.append({"role": "tool", "html": html})
            self._render_view()
        elif kind == "plan":
            steps = getattr(ev, "steps", None) or []
            if steps:
                lines = ["<p style='margin:4px 0;'><i>Plan:</i></p>"]
                for step in steps:
                    mark = {"pending": "○", "in_progress": "◐",
                            "completed": "●"}.get(getattr(step, "status", ""),
                                                  "•")
                    lines.append(
                        f"<p style='margin:2px 0;margin-left:12px;'><i>"
                        f"{mark} {self._html_escape(step.title)}</i></p>")
                self._messages.append(
                    {"role": "plan", "html": "\n".join(lines)})
                self._render_view()
        elif kind == "usage":
            used = getattr(ev, "used", 0)
            size = getattr(ev, "size", 0)
            if size:
                html = (f"<p style='margin:2px 0;color:#888;'><i>"
                        f"[context: {used}/{size} tokens]</i></p>")
                self._messages.append({"role": "usage", "html": html})
                self._render_view()
        elif kind == "task":
            title = getattr(ev, "title", "")
            status = getattr(ev, "status", "")
            if title:
                html = (f"<p style='margin:2px 0;'><i>⟡ "
                        f"{self._html_escape(title)}: "
                        f"{self._html_escape(status)}</i></p>")
                self._messages.append({"role": "task", "html": html})
                self._render_view()

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
        # Finalise the assistant reply: render the accumulated raw markdown
        # as proper HTML via Qt's markdown parser.
        if self._assistant_text:
            rendered = self._md_to_html(self._assistant_text)
            if self._messages and self._messages[-1].get("role") == "assistant" \
                    and self._messages[-1].get("streaming"):
                self._messages[-1]["html"] = rendered
                self._messages[-1]["streaming"] = False
            else:
                self._messages.append(
                    {"role": "assistant", "html": rendered, "streaming": False})
            self._assistant_text = ""
            self._render_view()
        if reason and reason != "done":
            self._messages.append(
                {"role": "system", "html": f"<i>({self._html_escape(reason)})</i>"})
            self._render_view()
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
        self._assistant_text = ""
        self._messages.append({
            "role": "system",
            "html": f"<i>error: {self._html_escape(message)}</i>",
        })
        self._render_view()
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
        self._assistant_text = ""
        self._messages.append({
            "role": "user",
            "html": self._html_escape(question),
        })
        self._render_view()
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
