#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server exposing an OpenGEODE SDL model to remote control.

Orbit (or any MCP client) starts this program and speaks the Model
Context Protocol over its stdin/stdout: newline-delimited JSON-RPC 2.0,
the local transport, with no socket and no third-party SDK — the same
wire orbit's own client speaks. The server implements the slice orbit
uses: the ``initialize`` handshake, ``tools/list`` and ``tools/call``.

The model is the one OpenGEODE edits, so the server works on the real
.pr files: it parses them, renders the SDL scene with OpenGEODE's own
renderer (headless: QT_QPA_PLATFORM=offscreen), and every modification
is written back to disk with OpenGEODE's own serialiser. The editor
picks the change up through its existing external-modification monitor.

Tools
-----
``list_symbols``     enumerate a scene's symbols (kind, text, position)
``find_symbol``      locate symbols by kind/text/position filters
``get_symbol``       one symbol's full detail (text, position, children)
``add_symbol``       insert a symbol: floating, chained below a parent
                     (vertical) or branched beside siblings (horizontal)
``remove_symbol``    delete a symbol (undoable through the scene's stack)
``set_symbol_text``  edit a symbol's text, with a syntax check
``move_symbol``      change a symbol's position
``check_model``      full syntax + semantic check, errors back as text
``check_syntax``     syntax-check a single symbol
``save_model``       write the modified model back to the .pr file(s)
``reload_model``     re-read the .pr files, adopting the editor's saves
``model_status``     files loaded, external changes, last parse result

Security
--------
The server never evaluates command input: every tool argument is
validated against a fixed whitelist (symbol kinds, scene names,
element names) and a JSON Schema published in ``tools/list``; model
text is data, set as text. Arguments of the wrong shape are rejected
with INVALID_PARAMS, never coerced. The only files the server touches
are the .pr/.asn files it was opened with, in the directory it was
started in — it does not follow paths coming from tool arguments.
"""

import json
import os
import re
import sys

# The scene work needs a Qt application. Headless, offscreen, and done
# before importing the modules that create widgets.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from opengeode import (Pr, Helper, ogAST, ogParser, sdlSymbols,  # noqa: E402
                       undoCommands)
from opengeode.opengeode import SDL_Scene, G_SYMBOLS  # noqa: E402

# The MCP protocol revision this server speaks (orbit proposes the same).
PROTOCOL_VERSION = "2025-06-18"

# Appended to every tool description when the calls are forwarded to a
# running editor, so the model knows it is editing the OPEN model.
LIVE_SUFFIX = (" [This runs against the model currently open in the "
               "OpenGEODE editor: changes appear there immediately and "
               "are undoable there.]")

# JSON-RPC error codes used below.
INVALID_PARAMS = -32602
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603

#: Symbol kinds a tool may name — the exact set the renderer can place.
#: kind → (class, needs_parent). A wrong kind is rejected, never guessed.
SYMBOL_KINDS = {
    "input":             (sdlSymbols.Input, True),
    "connect":           (sdlSymbols.Connect, True),
    "output":           (sdlSymbols.Output, True),
    "decision":          (sdlSymbols.Decision, True),
    "alternative":       (sdlSymbols.Alternative, True),
    "decision_answer":   (sdlSymbols.DecisionAnswer, True),
    "join":              (sdlSymbols.Join, True),
    "procedure_stop":    (sdlSymbols.ProcedureStop, True),
    "process_stop":      (sdlSymbols.ProcessStop, True),
    "label":             (sdlSymbols.Label, False),
    "task":              (sdlSymbols.Task, True),
    "procedure_call":    (sdlSymbols.ProcedureCall, True),
    "create":            (sdlSymbols.Create, True),
    "text":              (sdlSymbols.TextSymbol, False),
    # State is dual-role: floating it is a state box, parented it is
    # the NEXTSTATE terminator of a transition (None = both allowed).
    "state":             (sdlSymbols.State, None),
    "procedure":         (sdlSymbols.Procedure, False),
    "process":           (sdlSymbols.Process, False),
    "process_type":       (sdlSymbols.ProcessType, False),
    "start":             (sdlSymbols.Start, False),
    "procedure_start":   (sdlSymbols.ProcedureStart, False),
    "state_start":       (sdlSymbols.StateStart, False),
    "continuous_signal": (sdlSymbols.ContinuousSignal, True),
}

#: The kind name of every symbol class (the reverse of the table above,
#: plus the read-only kinds the renderer can place but a tool cannot
#: add): class → kind. Built once, so _kind_of never guesses by
#: mangling a class name.
_KIND_OF = {}
for _kind, (_cls, _needs_parent) in SYMBOL_KINDS.items():
    _KIND_OF.setdefault(_cls, _kind)
_KIND_OF[sdlSymbols.Comment] = "comment"       # placed by the editor only

#: Kinds that are removed only with ``force``: they carry a whole
#: sub-diagram the caller may not realise is going away.
CONTAINER_KINDS = {"state", "procedure", "process"}

#: The single elements parseSingleElement accepts (ogParser's whitelist),
#: kept here so the server can answer check_syntax without importing the
#: parser's private constant. Names are the parser's own grammar names.
SINGLE_ELEMENTS = [
    "input_part", "output", "decision", "alternative", "alternative_part",
    "terminator_statement", "label", "task", "procedure_call",
    "create_request", "end", "text_area", "content", "state", "start",
    "procedure", "floating_label", "connect_part", "process_definition",
    "synonym_definition", "proc_start", "state_start", "signalroute",
    "stop_if", "continuous_signal", "composite_state", "n7s_scl",
]

#: The grammar keyword that precedes an element's text in the .pr file
#: (what Pr.generate emits: "output restart;" has text "restart"). An
#: agent validating text BEFORE adding a symbol naturally sends the bare
#: text (what add_symbol will store), not the full statement — and the
#: parser needs the full one. This map turns the bare form into the
#: complete statement the grammar accepts. Elements whose grammar rule
#: expects the whole construct (state needs its content; label takes a
#: "name:" form; decision needs its answers) are not listed: for those,
#: the full text is the only valid input and the skill says so.
_ELEMENT_KEYWORD = {
    "input_part": "input",
    "output": "output",
    "task": "task",
    "procedure_call": "call",
    "continuous_signal": "provided",
    "connect_part": "connect",
    "stop_if": "stop",
    "floating_label": "",
    # The NEXTSTATE terminator: the editor stores the state name and
    # Pr.generate emits "NEXTSTATE Wait;". (Other terminator forms —
    # join, stop, return — carry their own keyword in the text.)
    "terminator_statement": "NEXTSTATE",
}

#: Elements where a bare-text form exists only inside the full construct
#: (state needs its branches; label is "name:" in a branch; decision
#: needs answers; terminator_statement's NEXTSTATE form does parse
#: bare). check_syntax accepts the bare text for the first group by
#: completing it, and the skill documents the full form for the rest.
_FULL_TEXT_ELEMENTS = {"state", "label", "decision", "alternative",
                       "alternative_part", "content", "text_area",
                       "procedure", "process_definition", "composite_state",
                       "start", "proc_start", "state_start", "end"}


def _complete_element_text(element, text):
    """The text the grammar accepts for a single-element check: the
    bare text an agent sends (what add_symbol stores) completed into
    the full statement when the element's grammar needs the keyword.

    The editor stores a symbol's bare text ("test = 0" for a continuous
    signal) and Pr.generate re-adds the keyword when serialising
    ("provided test = 0;"). check_syntax is the validation half of an
    add: it must accept exactly the text add_symbol will store, so the
    keyword is re-added here the same way."""
    if element in _FULL_TEXT_ELEMENTS or not text:
        return text
    kw = _ELEMENT_KEYWORD.get(element)
    if kw is None:
        return text
    if kw:
        return f"{kw} {text};"
    return f"{text};"


def _kind_of(symbol):
    """The whitelisted kind name of a scene symbol, or None for symbols
    outside the whitelist (connections, grabbers)."""
    return _KIND_OF.get(type(symbol))


class SdlModel:
    """The SDL model under control: the parsed AST, the rendered scenes,
    and the operations on them. One model, loaded once at startup; the
    tools mutate it and save it back."""

    def __init__(self, pr_files):
        # QApplication must exist before any SDL_Scene is created.
        self.app = QApplication.instance() or QApplication([])
        self.pr_files = [os.path.abspath(f) for f in pr_files]
        if not self.pr_files:
            raise ValueError("no .pr file given: open the MCP server in "
                             "the directory of the model")
        for path in self.pr_files:
            if not os.path.isfile(path):
                raise ValueError(f"model file not found: {path}")
        # parse_pr resolves the model's USE (ASN.1) clauses relative to
        # the CWD — the GUI does the same chdir before parsing.
        self.model_dir = os.path.dirname(self.pr_files[0]) or "."
        self._cwd = os.getcwd()
        os.chdir(self.model_dir)
        try:
            self.reload()
        finally:
            os.chdir(self._cwd)
        self._symbol_ids = {}   # int handle → (scene, symbol) for tools
        self._scene_names = {}  # id(scene) → reported scene name
        # The files' state as this server last saw them, so a save can
        # refuse to clobber changes made since (the editor reloads from
        # disk; this server is not the same process as the editor).
        self._mtimes = self._disk_mtimes()

    # -- loading and scenes -------------------------------------------------

    def _disk_mtimes(self):
        """The current mtimes of the model files on disk."""
        out = {}
        for path in self.pr_files:
            try:
                out[path] = os.path.getmtime(path)
            except OSError:
                out[path] = None
        return out

    def external_changes(self):
        """Files changed on disk since this server last loaded or saved
        them — the editor (another process) saved its own edits, and
        this server's in-memory model is now stale. A save from here
        would CLOBBER those edits; reload_model() picks them up instead."""
        current = self._disk_mtimes()
        return [path for path in self.pr_files
                if (self._mtimes.get(path), current.get(path))
                    != (None, None)
                and self._mtimes.get(path) != current.get(path)]

    def refresh_mtimes(self):
        """Record the on-disk state after this server's own save."""
        self._mtimes = self._disk_mtimes()

    def reload(self):
        """(Re)parse the .pr files and render the block scene. Must be
        called with the CWD already set to the model directory."""
        ast, warnings, errors = ogParser.parse_pr(files=self.pr_files)
        self.ast = ast
        self.parse_errors = errors
        self.parse_warnings = warnings
        # The GUI's own load recipe (opengeode.py:2652-2674): a process
        # referenced from the system structure must come from
        # ast.processes, not from the empty block placeholder.
        try:
            syst, = ast.systems
            block, = syst.blocks
            if block.processes and block.processes[0].referenced:
                block.processes = list(ast.processes)
        except ValueError:
            block = ogAST.Block()
            block.processes = list(ast.processes)
        # Atomic: render into temporaries and commit only on success, so
        # a model that cannot be rendered (broken by an editor save, say)
        # leaves the previous model intact and the server alive.
        scene = SDL_Scene(context="block")
        scene.render_everything(block)
        self.block = block
        self.scene = scene
        # The scene's AST drives the ASN.1 header of a full-model
        # serialisation (Pr.asn1_header reads scene.ast.use_clauses):
        # keep it current with the parse the scene was built from.
        scene.ast = ast

    def _scene_name_of(self, scene):
        """The scene's name as the tools report it, building it on the
        fly when scenes() has not been called yet for this scene."""
        self.scenes()                     # populates _scene_names
        return self._scene_names.get(id(scene),
                                     getattr(scene, "name", "") or "scene")

    def scenes(self):
        """Every scene keyed by name: 'block', 'process og', 'state
        wait', … — built from the symbol hierarchy, with each scene's
        context prefix. Also records the name of every scene for
        symbol_info. (The GUI's scene.path is not used: it strips three
        trailing characters of the scene name, which eats short names.)"""
        out = {"block": self.scene}
        self._scene_names = {id(self.scene): "block"}
        seen = {id(self.scene)}

        def visit(scene, path):
            for symb in scene.visible_symb:
                sub = getattr(symb, "nested_scene", None)
                if not isinstance(sub, SDL_Scene) or id(sub) in seen:
                    continue
                seen.add(id(sub))
                name = str(symb).strip().lower() or "scene"
                context = (getattr(sub, "context", "") or "").strip().lower()
                key = f"{context} {name}".strip()
                out[key] = sub
                # The bare name ('og', 'wait') when it is free.
                out.setdefault(name, sub)
                # The full path form ('process og state wait').
                full = " ".join(path + [key])
                out.setdefault(full, sub)
                self._scene_names[id(sub)] = full
                visit(sub, path + [key])

        visit(self.scene, [])
        # A scene's own name is its full path from scenes(); the bare
        # block scene is always reachable as 'block'.
        return out

    def scene_named(self, name):
        """A scene by name, with the block scene as the default. Accepts
        the full path ('process og state wait'), a single key ('process
        og'), or a bare name ('og', 'wait')."""
        if name in (None, "", "block"):
            return self.scene
        scenes = self.scenes()
        key = name.strip().lower()
        if key in scenes:
            return scenes[key]
        # A bare or partial name: match the tail of a full path ('wait'
        # matches 'process og state wait'; 'og' matches 'process og').
        tail = " " + key
        matches = [sc for k, sc in scenes.items()
                   if k == key or k.endswith(tail)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"ambiguous scene name: {name}")
        raise ValueError(f"no such scene: {name}")

    # -- symbol table -------------------------------------------------------

    def _register(self, scene, symbol):
        handle = id(symbol)
        self._symbol_ids[handle] = (scene, symbol)
        return handle

    def symbols(self, scene=None):
        """Every visible symbol of a scene, most-parent-first order."""
        scene = scene or self.scene
        out = []
        for symb in scene.visible_symb:
            kind = _kind_of(symb)
            if kind is None:        # a connection or grabber, not a symbol
                continue
            out.append(self._symbol_info(symb, scene))
        return out

    def _symbol_info(self, symb, scene, with_children=True):
        info = {
            "id": str(id(symb)),
            "kind": _kind_of(symb),
            "text": str(symb),
            "scene": self._scene_name_of(scene),
            "x": round(symb.scenePos().x(), 1),
            "y": round(symb.scenePos().y(), 1),
            "has_parent": bool(symb.hasParent),
        }
        # Connections (channels between processes, signalroutes to the
        # environment) are items of the block scene, not children: they
        # are reported as "connections" of the symbol they start from.
        conns = [c for c in self._connections_of(scene)
                 if getattr(c, "parent", None) is symb
                 or getattr(c, "child", None) is symb]
        if conns:
            info["connections"] = [self._connection_info(c, scene)
                                   for c in conns]
        parent = symb.parent if symb.hasParent else None
        if parent is not None:
            info["parent_id"] = str(id(parent))
        if getattr(symb, "nested_scene", None) is not None:
            info["nested_scene"] = self._scene_name_of(symb.nested_scene)
        self._register(scene, symb)
        if with_children:
            info["children"] = [self._symbol_info(c, scene, False)
                                for c in symb.childSymbols()
                                if _kind_of(c)]
        return info

    def _connections_of(self, scene):
        """The Channels/Signalroutes of a scene: they are scene items,
        not symbols, so visible_symb never yields them."""
        from . import Connectors
        return [item for item in scene.items()
                if isinstance(item, Connectors.Signalroute)]

    def _connection_info(self, conn, scene):
        """A Channel/Signalroute as tool data: its endpoints, the signal
        lists, and a handle the connection tools accept."""
        parent = getattr(conn, "parent", None)
        child = getattr(conn, "child", None)
        is_channel = child is not None and child is not parent
        info = {
            "id": str(id(conn)),
            "kind": "channel" if is_channel else "signalroute",
            "text": f"{str(parent)} → "
                    f"{str(child) if is_channel else 'env'}",
            "scene": self._scene_name_of(scene),
        }
        if parent is not None:
            info["from_id"] = str(id(parent))
        if is_channel:
            info["to_id"] = str(id(child))
        if getattr(conn, "out_sig", ""):
            info["out_signals"] = conn.out_sig
        if getattr(conn, "in_sig", ""):
            info["in_signals"] = conn.in_sig
        self._register(scene, conn)
        return info

    def symbol_by_handle(self, handle):
        """The (scene, symbol) a tool's handle refers to, verifying the
        symbol still lives on its scene."""
        try:
            scene, symb = self._symbol_ids[int(handle)]
        except (KeyError, ValueError):
            raise ValueError(f"unknown symbol id: {handle}")
        if symb.scene() is not scene or not symb.isVisible():
            raise ValueError(f"symbol is gone: {handle}")
        return scene, symb

    # -- lookup -------------------------------------------------------------

    def find(self, scene=None, kind=None, text_contains=None,
             near=None, max_results=50):
        """Symbols matching filters; each result carries the id tools use."""
        scene = scene or self.scene
        results = []
        for info in self.symbols(scene):
            if kind and info["kind"] != kind:
                continue
            if (text_contains is not None
                    and text_contains.lower() not in info["text"].lower()):
                continue
            if near:
                dist = ((info["x"] - near[0]) ** 2
                        + (info["y"] - near[1]) ** 2) ** 0.5
                info["distance"] = round(dist, 1)
            results.append(info)
        if near:
            results.sort(key=lambda i: i["distance"])
        return results[:max_results]

    # -- modification -------------------------------------------------------

    def add(self, kind, scene_name=None, parent_id=None, text=None,
            x=None, y=None):
        """Insert a symbol. With a parent: below it (vertical chain) or
        branched among its siblings (horizontal). Without: floating, at
        (x, y) in the named scene."""
        if kind not in SYMBOL_KINDS:
            raise ValueError(f"unknown symbol kind: {kind}")
        cls, needs_parent = SYMBOL_KINDS[kind]
        parent = None
        if parent_id is not None:
            parent_scene, parent = self.symbol_by_handle(parent_id)
            # The parent decides the scene: a chain or branch insertion
            # goes where the parent is. The 'scene' argument is for
            # floating symbols.
            scene = parent_scene
        else:
            scene = self.scene_named(scene_name)
        if needs_parent is True and parent is None:
            raise ValueError(f"{kind} needs a parent symbol")
        if needs_parent is False and parent is not None:
            raise ValueError(f"{kind} is a floating symbol; "
                             "it cannot take a parent")
        # The class' own follower rules are the authority on placement:
        # they mirror what the editor's toolbar allows. A NEXTSTATE
        # (parented state) follows only a chain's LAST symbol — the rule
        # rejects adding one mid-chain or after an existing terminator.
        if parent is not None:
            allowed = parent.allowed_followers
            if cls.__name__ not in allowed and cls not in allowed:
                if not any(cls.__name__ == a for a in allowed) \
                        and not any(isinstance(a, str) and
                                    cls.__name__ == a for a in allowed):
                    raise ValueError(
                        f"{_kind_of(parent)} cannot be followed by {kind}")
        item = cls()
        scene.addItem(item)
        item.insert_symbol(parent, x, y)
        item.show()
        try:
            item.grabber.display()
        except AttributeError:
            pass        # floating symbols without a grabber
        item.update_connections()
        if parent is None:
            G_SYMBOLS.add(item)     # keep it alive, as place_symbol does
        if text is not None and getattr(item, "has_text_area", True):
            item.text.setPlainText(text)
            item.ast.inputString = text
            item.text.try_resize()
        # A decision comes with answers; a container opens a sub-scene.
        if cls is sdlSymbols.Decision:
            for _ in range(2):
                self.add("decision_answer", parent_id=str(id(item)),
                         text="answer")
        elif cls is sdlSymbols.Procedure or cls is sdlSymbols.Process \
                or (cls is sdlSymbols.State and parent is None):
            # Containers get their sub-scene, the way place_symbol
            # does (Procedure, State, Process). A PARENTED State is the
            # NEXTSTATE terminator of a transition — no sub-scene, just
            # the line and arrow.
            item.nested_scene = scene.create_subscene(
                    cls.__name__.lower(), scene)
            item.nested_scene.name = str(item)
        scene.scene_refresh()
        return self._symbol_info(item, scene)

    def remove(self, handle, force=False):
        """Delete a symbol through the scene's undo stack (reversible in
        the editor's sense: hide, never removeItem — the GUI convention
        that avoids the exit crash)."""
        scene, symb = self.symbol_by_handle(handle)
        kind = _kind_of(symb)
        if kind in CONTAINER_KINDS and not force:
            raise ValueError(
                f"{kind} carries a whole sub-diagram; pass force=true "
                "to delete it with its content")
        scene.undo_stack.push(undoCommands.DeleteSymbol(item=symb))
        scene.scene_refresh()
        return {"removed": kind, "text": str(symb)}

    def set_text(self, handle, text):
        """Set a symbol's text — the editor's canonical update (text,
        AST, size) — and return the syntax check of the new text."""
        scene, symb = self.symbol_by_handle(handle)
        if not getattr(symb, "has_text_area", False):
            raise ValueError(f"{_kind_of(symb)} has no text to set")
        symb.text.setPlainText(text)
        symb.ast.inputString = text
        symb.text.try_resize()
        scene.scene_refresh()
        return {"kind": _kind_of(symb), "text": str(symb)}

    def move(self, handle, x, y):
        """Move a symbol to scene coordinates (x, y)."""
        scene, symb = self.symbol_by_handle(handle)
        symb.pos_x = x
        symb.pos_y = y
        symb.update_connections()
        scene.scene_refresh()
        return {"kind": _kind_of(symb), "x": x, "y": y}

    # -- signal declarations (block scene text areas) ------------------------

    def add_signal_declaration(self, signal, param_type=None):
        """Declare a signal in the block scene's signal-declaration text
        area (or create it). The declaration is a full SDL statement:
        'signal <name>(<param_type>);' — the block scene text area is
        where the parser finds SIGNALs referenced by connections."""
        scene = self.scene
        # find the existing signal-declaration text area (contains
        # 'signal' lines) or create one
        text_area = None
        for symb in scene.texts:
            content = str(symb)
            if content.strip().lower().startswith("signal"):
                text_area = symb
                break
        if text_area is None:
            item = sdlSymbols.TextSymbol()
            scene.addItem(item)
            item.insert_symbol(None, 400, 10)
            G_SYMBOLS.add(item)
            text_area = item
        decl = (f"signal {signal}"
                + (f"({param_type})" if param_type else "")
                + ";")
        content = str(text_area)
        content = (content + "\n" + decl).strip()
        text_area.text.setPlainText(content)
        text_area.ast.inputString = content
        text_area.text.try_resize()
        scene.scene_refresh()
        return {"declared": decl}

    def list_signals(self):
        """Every signal declared in the block scene's text areas."""
        signals = []
        for symb in self.scene.texts:
            for line in str(symb).split("\n"):
                line = line.strip()
                if line.lower().startswith("signal ") and line.endswith(";"):
                    signals.append(line[:-1])
        return {"signals": signals}

    # -- connections (channels, signalroutes) --------------------------------

    def add_connection(self, kind, from_id, to_id=None, out_signals=(),
                       in_signals=(), via=None):
        """Create a Channel (process to process) or a Signalroute
        (process to the environment) — the block-scene connectors that
        carry a model's signals. ``from_id`` is the process the
        connection starts from; ``to_id`` the process it ends at (a
        Channel); without it the connection goes to the environment (a
        Signalroute). ``out_signals`` are the signals from ``from_id``
        to the other end, ``in_signals`` the ones coming back;
        ``via`` is an optional list of [x, y] waypoints between them."""
        from . import Connectors
        scene, start = self.symbol_by_handle(from_id)
        end = None
        if to_id is not None:
            end_scene, end = self.symbol_by_handle(to_id)
            if end_scene is not scene:
                raise ValueError("both ends of a connection must be in "
                                 "the same scene")
        if kind == "channel" and end is None:
            raise ValueError("a channel needs to_id (process to process); "
                             "use kind signalroute for the environment")
        if kind == "signalroute" and end is not None:
            raise ValueError("a signalroute goes to the environment; "
                             "use kind channel between two processes")
        if end is not None and end is start:
            raise ValueError("a channel needs two different processes")
        if end is not None:
            conn = Connectors.Channel(parent=start, child=end)
        else:
            conn = Connectors.Signalroute(parent=start)
        # Signal lists: the labels carry them (the GUI's convention)
        if out_signals:
            conn.out_sig = ", ".join(out_signals)
        if in_signals:
            conn.in_sig = ", ".join(in_signals)
        self._decorate_connection(conn, out_signals, in_signals)
        # Optional waypoints, in scene coordinates, between the ends
        if via:
            conn.middle_points = [QPointF(*map(float, pt)) for pt in via]
        # The connector is parented to a scene symbol, so it is already
        # in the scene — only add it when it is not.
        if conn.scene() is not scene:
            scene.addItem(conn)
        scene.undo_stack.push(undoCommands.InsertConnection(conn, scene))
        scene.scene_refresh()
        return self._connection_info(conn, scene)

    def set_connection_signals(self, conn_id, out_signals=None,
                               in_signals=None):
        """Change the signal lists of a connection. Each argument is a
        list of signal names; None leaves that side untouched."""
        scene, conn = self.connection_by_handle(conn_id)
        if out_signals is not None:
            conn.out_sig = ", ".join(out_signals)
        if in_signals is not None:
            conn.in_sig = ", ".join(in_signals)
        self._decorate_connection(
            conn,
            conn.out_sig.split(", ") if conn.out_sig else (),
            conn.in_sig.split(", ") if conn.in_sig else ())
        conn.reshape()
        scene.scene_refresh()
        return self._connection_info(conn, scene)

    def remove_connection(self, conn_id):
        """Delete a channel/signalroute through the scene's undo stack."""
        scene, conn = self.connection_by_handle(conn_id)
        scene.undo_stack.push(undoCommands.DeleteConnection(conn, scene))
        scene.scene_refresh()
        return {"removed": True,
                "kind": ("channel" if type(conn).__name__ == "Channel"
                         else "signalroute")}

    def _decorate_connection(self, conn, out_signals, in_signals):
        """Set the labels the way the editor does: '[sig1, sig2]'."""
        out_txt = f'[{", ".join(out_signals)}]' if out_signals else "[]"
        in_txt = f'[{", ".join(in_signals)}]' if in_signals else "[]"
        conn.label_out.setPlainText(out_txt)
        conn.label_in.setPlainText(in_txt)

    def connection_by_handle(self, handle):
        """The (scene, connection) a handle refers to, searched among
        the scenes' connectors."""
        h = str(handle)
        for name, scene in self.scenes().items():
            for conn in self._connections_of(scene):
                if str(id(conn)) == h:
                    return scene, conn
        raise ValueError("unknown or gone connection: " + h)

    # -- checks and saving --------------------------------------------------

    def check_model(self):
        """The GUI's own check, headless: per-symbol syntax, then the full
        semantic parse of the serialised model. Returns errors and
        warnings as text lines, each tagged with where it comes from."""
        errors = []
        warnings = []
        # Syntax, per symbol — a bad symbol is caught precisely, without
        # the whole model's parse drowning it out.
        for name, scene in self.scenes().items():
            for symb in scene.visible_symb:
                try:
                    errs = scene.syntax_errors(symb)
                except Exception:
                    errs = []
                for e in errs or []:
                    errors.append(f"syntax [{name}] {str(symb)[:40]}: {e}")
        # Semantics, the way check_model does it: serialise the block
        # scene and parse it together with the read-only companion files.
        sem_errors, sem_warnings = self._semantic_check()
        errors.extend(f"semantic {line}" for line in sem_errors)
        warnings.extend(f"semantic {line}" for line in sem_warnings)
        return {"status": "Done" if not errors else "Errors",
                "errors": errors,
                "warnings": warnings,
                "error_count": len(errors),
                "warning_count": len(warnings)}

    def _semantic_check(self):
        """Serialise and re-parse, mirroring SDL_View.check_model. The
        .pr files the model was opened with, minus the one being saved,
        are parsed from disk alongside the serialised text so types and
        signals defined there resolve."""
        saved = {os.path.basename(p) for p in self.pr_files}
        readonly = [p for p in self.pr_files
                    if os.path.basename(p) not in {os.path.basename(f)
                                                   for f in saved}]
        # The serialisation needs the model's USE clauses (the ASN.1
        # header): seed the scene's AST with the one the model was
        # loaded with — the re-parse below refreshes it afterwards.
        if getattr(self.scene, 'ast', None) is None:
            self.scene.ast = self.ast
        pr_raw = Pr.parse_scene(self.scene, full_model=self._full_model())
        pr_data = "\n".join(pr_raw)
        if not pr_data:
            return [], []
        self._cwd = os.getcwd()
        os.chdir(self.model_dir)
        try:
            ast, warnings, errs = ogParser.parse_pr(
                    files=[p for p in self.pr_files
                           if p != self._main_file()],
                    string=pr_data)
        finally:
            os.chdir(self._cwd)
        self.ast = ast
        self.scene.ast = ast
        return [e.msg for e in errs], [w.msg for w in warnings]

    def _main_file(self):
        """The .pr file the block scene is saved to: the one whose name
        matches the block (the GUI's convention); failing that, the
        first file that is not the system structure companion
        (system_structure.pr, the naming convention everywhere in the
        testsuite and TASTE); failing that, the first file. Never
        silently overwrite a companion with process content."""
        block_name = str(getattr(self.block, "name", "") or "").strip().lower()
        if block_name:
            for path in self.pr_files:
                stem = os.path.splitext(os.path.basename(path))[0].lower()
                if stem == block_name:
                    return path
        for path in self.pr_files:
            stem = os.path.splitext(os.path.basename(path))[0].lower()
            if not stem.startswith("system_structure"):
                return path
        return self.pr_files[0]

    def _full_model(self):
        """True when the model is a single .pr file holding the whole
        system (the serialiser must then emit system/block wrappers);
        False for the common case of a process file with a companion
        system_structure.pr."""
        return len(self.pr_files) == 1

    def check_syntax(self, element, text, context=""):
        """Syntax-check one SDL element by its grammar name, with the
        parser's own single-element API. Used to validate text before it
        ever reaches the model."""
        if element not in SINGLE_ELEMENTS:
            raise ValueError(f"unknown element: {element}")
        # Accept the bare text add_symbol will store (the agent's
        # natural input): complete it into the full statement the
        # grammar parses. When the bare form does not parse, the raw
        # text is tried too so a full statement still validates.
        completed = _complete_element_text(element, text)
        self._cwd = os.getcwd()
        os.chdir(self.model_dir)
        try:
            _, syntax_errors, semantic_errors, warnings, _ = \
                ogParser.parseSingleElement(elem=element, string=completed,
                                            context=self._context(context))
            if syntax_errors and completed != text:
                _, raw_errors, raw_sem, raw_warn, _ = \
                    ogParser.parseSingleElement(elem=element, string=text,
                                                context=self._context(
                                                    context))
                if not raw_errors:
                    syntax_errors, semantic_errors, warnings = \
                        raw_errors, raw_sem, raw_warn
        finally:
            os.chdir(self._cwd)
        return {"syntax_errors": syntax_errors,
                "semantic_errors": [str(e) for e in semantic_errors],
                "warnings": [str(w) for w in warnings]}

    def _context(self, name):
        """The process AST to check an element against: the model's own
        process, or a fresh dummy like the parser does on its own."""
        if name:
            for proc in self.ast.processes:
                if proc.processName.lower() == name.lower():
                    return proc
        return self.ast.processes[0] if self.ast.processes else None

    def save(self, force=False):
        """Write the model back to the .pr file(s), mirroring the GUI's
        save_diagram: translate to a non-negative coordinate origin,
        serialise, and write. The editor reloads the file on its own.
        Refuses (unless force) when the file changed on disk since it was
        last loaded — the editor's own save must not be clobbered by a
        stale in-memory model."""
        changed = self.external_changes()
        if changed and not force:
            raise ValueError(
                "the model file(s) changed on disk since this server "
                "loaded them (probably saved by the editor): "
                + ", ".join(os.path.basename(p) for p in changed)
                + " — call reload_model first (or save_model with "
                  "force: true) to keep the on-disk version")
        scene = self.scene
        # Coordinates must be non-negative for a clean reload
        scene.translate_to_origin()
        # A companion model whose block scene holds MORE than one process
        # definition cannot be saved the way the GUI does (the
        # serialiser emits only the first process — the rest would be
        # lost). In that case each process goes to its own .pr file and
        # the system structure is regenerated into the companion with
        # REFERENCED processes — the TASTE convention.
        procs = [s for s in scene.processes
                 if ":" not in str(s)]
        if not self._full_model() and len(procs) > 1:
            return self._save_multi_process(scene, procs)
        pr_raw = Pr.parse_scene(scene, full_model=self._full_model())
        pr_data = "\n".join(pr_raw)
        # The GUI writes the process file; the system structure, when
        # there is one, is read-only and untouched.
        target = self._main_file()
        with open(target, "w", encoding="utf-8") as f:
            f.write(pr_data)
        self.refresh_mtimes()
        return {"saved": os.path.basename(target), "bytes": len(pr_data)}

    def _save_multi_process(self, scene, procs):
        """A companion model with several process definitions: write
        each process to <name>.pr and regenerate the system structure
        into the companion, with the processes REFERENCED (the TASTE
        convention: structure in one file, definitions in theirs)."""
        written = []
        for proc in procs:
            name = str(proc).strip().lower()
            # The process' own file: the main file when the name
            # matches, else <name>.pr next to it.
            main = self._main_file()
            main_stem = os.path.splitext(os.path.basename(main))[0].lower()
            target = main if name == main_stem else os.path.join(
                self.model_dir, name + ".pr")
            pr_raw = list(Pr.generate(proc))
            with open(target, "w", encoding="utf-8") as f:
                f.write("\n".join(pr_raw))
            written.append(os.path.basename(target))
            if target not in self.pr_files:
                self.pr_files.append(target)
        # Regenerate the structure: the full-model serialisation with
        # each process definition replaced by a REFERENCED declaration.
        scene.ast = self.ast
        full = Pr.parse_scene(scene, full_model=True)
        out, skip = [], None
        for line in full:
            stripped = line.strip()
            match = re.match(r"process (\S+);$", stripped)
            if match and not skip:
                out.append(line.replace(
                    f"process {match.group(1)};",
                    f"process {match.group(1)} REFERENCED;"))
                skip = match.group(1)
                continue
            if skip and stripped == f"endprocess {skip};":
                skip = None
                continue
            if not skip:
                out.append(line)
        structure = self._structure_file()
        # Preserve the companion's header up to and INCLUDING its system
        # declaration line (the ASN.1 reference and the system name);
        # the generated structure's own system line is dropped.
        header = ""
        if os.path.isfile(structure):
            with open(structure, encoding="utf-8") as f:
                orig = f.read()
            match = re.search(r"(?is)\A.*?^system\s+\S+\s*;",
                              orig, re.MULTILINE)
            if match:
                header = match.group(0)
        first_sys = next((i for i, l in enumerate(out)
                          if re.match(r"\s*system\s+\S+\s*;", l)), None)
        if header and first_sys is not None:
            struct_data = header + "\n" + "\n".join(out[first_sys + 1:])
        else:
            struct_data = "\n".join(out)
        with open(structure, "w", encoding="utf-8") as f:
            f.write(struct_data)
        written.append(os.path.basename(structure))
        self.refresh_mtimes()
        return {"saved": ", ".join(written),
                "bytes": sum(os.path.getsize(os.path.join(self.model_dir,
                                                          w))
                             for w in written)}

    def _structure_file(self):
        """The file holding the system structure of a companion model:
        the system_structure.pr convention; failing that, the file
        whose stem differs from the main file's."""
        for path in self.pr_files:
            stem = os.path.splitext(os.path.basename(path))[0].lower()
            if stem.startswith("system_structure"):
                return path
        main = self._main_file()
        for path in self.pr_files:
            if path != main:
                return path
        return main

    def reload_model(self):
        """Re-read the .pr files from disk, discarding this server's
        in-memory model. Use it when the editor saved its own changes:
        symbol ids from before the reload are invalid, so start again
        with list_symbols."""
        self._cwd = os.getcwd()
        os.chdir(self.model_dir)
        try:
            self.reload()
        finally:
            os.chdir(self._cwd)
        self._symbol_ids = {}
        self._scene_names = {}
        self.refresh_mtimes()
        return {"reloaded": [os.path.basename(p) for p in self.pr_files]}

    def model_status(self):
        """A quick health read of the model: what is loaded, whether the
        files changed on disk since (reload_model to pick them up), and
        the last parse outcome."""
        changed = self.external_changes()
        return {"files": [os.path.basename(p) for p in self.pr_files],
                "saved_to": os.path.basename(self._main_file()),
                "external_changes": [os.path.basename(p) for p in changed],
                "stale": bool(changed),
                "parse_errors": [e.msg for e in self.parse_errors],
                "parse_warnings": [w.msg for w in self.parse_warnings]}


# ---------------------------------------------------------------------------
# The tool catalogue: name → (description, JSON Schema, implementation).
# The schema is what orbit shows the model; the implementation is the
# only code a tool call can reach — the arguments have been validated by
# the schema and are re-validated by the implementation's own checks.
# ---------------------------------------------------------------------------

def _scene_arg():
    return {"type": "string",
            "description": "Scene by name: 'block', or a nested scene's "
                           "path ('process og', 'state wait'), or its last "
                           "word ('og', 'wait'). Default: block."}


def _id_arg():
    return {"type": "string",
            "description": "The symbol's id from list_symbols/find_symbol."}


def _build_tools(model):
    """The tool catalogue. With a model, each tool carries its
    implementation; with None (the live relay) the schemas are all
    that is needed — every call is forwarded to the editor."""
    tools = []

    def tool(name, description, schema, func):
        tools.append({"name": name,
                      "description": description,
                      "inputSchema": schema,
                      "_func": func})

    tool("list_symbols",
         "List the symbols of an SDL scene: kind, text, position, parent, "
         "children. The ids it returns are what the other tools take.",
         {"type": "object", "properties": {
             "scene": _scene_arg()},
          "additionalProperties": False},
         lambda args: model.symbols(model.scene_named(
             args.get("scene"))))

    tool("find_symbol",
         "Find symbols by filters: kind, text substring, or the ones "
         "closest to a position. Returns at most 'max_results'.",
         {"type": "object", "properties": {
             "scene": _scene_arg(),
             "kind": {"type": "string",
                      "enum": sorted(SYMBOL_KINDS),
                      "description": "Symbol kind to match."},
             "text_contains": {"type": "string",
                                "description": "Substring of the symbol's "
                                               "text, case-insensitive."},
             "near": {"type": "array", "items": {"type": "number"},
                      "minItems": 2, "maxItems": 2,
                      "description": "[x, y] scene coordinates; results "
                                     "are sorted by distance."},
             "max_results": {"type": "integer", "minimum": 1,
                              "maximum": 200, "default": 50}},
          "additionalProperties": False},
         lambda args: {"symbols": model.find(
             scene=model.scene_named(args.get("scene")),
             kind=args.get("kind"),
             text_contains=args.get("text_contains"),
             near=args.get("near"),
             max_results=args.get("max_results", 50))})

    tool("get_symbol",
         "One symbol's detail: kind, text, position, parent, children, "
         "and its nested scene when it has one.",
         {"type": "object", "properties": {
             "id": _id_arg()},
          "required": ["id"], "additionalProperties": False},
         lambda args: model._symbol_info(
             model.symbol_by_handle(args["id"])[1],
             model.symbol_by_handle(args["id"])[0]))

    tool("add_symbol",
         "Add a symbol. Give parent_id to insert it in a chain (below a "
         "vertical parent: task, output, decision…) or a branch (under a "
         "state, an answer, a decision): the symbol class decides. "
         "Without parent_id the symbol is floating, placed at (x, y) in "
         "the scene. 'text' is the symbol's SDL text; it is set as-is "
         "after a syntax check of the placed symbol.",
         {"type": "object", "properties": {
             "kind": {"type": "string", "enum": sorted(SYMBOL_KINDS)},
             "scene": _scene_arg(),
             "parent_id": _id_arg(),
             "text": {"type": "string",
                      "description": "The symbol's SDL text "
                                      "(e.g. 'x := x + 1')."},
             "x": {"type": "number"},
             "y": {"type": "number"}},
          "required": ["kind"], "additionalProperties": False},
         lambda args: model.add(args["kind"],
                                scene_name=args.get("scene"),
                                parent_id=args.get("parent_id"),
                                text=args.get("text"),
                                x=args.get("x"), y=args.get("y")))

    tool("remove_symbol",
         "Delete a symbol (the scene's undo stack, so the editor can "
         "undo it). Deleting a state or procedure removes its whole "
         "sub-diagram — pass force=true to confirm.",
         {"type": "object", "properties": {
             "id": _id_arg(),
             "force": {"type": "boolean", "default": False}},
          "required": ["id"], "additionalProperties": False},
         lambda args: model.remove(args["id"], args.get("force", False)))

    tool("set_symbol_text",
         "Change a symbol's text (its SDL statement). The new text is "
         "applied and the symbol's syntax is checked; the result reports "
         "any errors so they can be fixed before saving.",
         {"type": "object", "properties": {
             "id": _id_arg(),
             "text": {"type": "string"}},
          "required": ["id", "text"], "additionalProperties": False},
         lambda args: model.set_text(args["id"], args["text"]))

    tool("move_symbol",
         "Move a symbol to absolute scene coordinates (x, y).",
         {"type": "object", "properties": {
             "id": _id_arg(),
             "x": {"type": "number"},
             "y": {"type": "number"}},
          "required": ["id", "x", "y"], "additionalProperties": False},
         lambda args: model.move(args["id"], args["x"], args["y"]))

    tool("add_signal_declaration",
         "Declare a signal in the block scene (its signal-declaration "
         "text area): 'signal <name>' or 'signal <name>(<param_type>)'. "
         "Signals must be declared before channels/signalroutes can "
         "carry them. The param_type is an ASN.1 type name from the "
         "data view.",
         {"type": "object", "properties": {
             "signal": {"type": "string",
                        "description": "Signal name, e.g. 'go'."},
             "param_type": {"type": "string",
                            "description": "Optional ASN.1 type of the "
                                           "signal parameter, e.g. "
                                           "'My_OctStr'."}},
          "required": ["signal"], "additionalProperties": False},
         lambda args: model.add_signal_declaration(
             args["signal"], args.get("param_type")))

    tool("list_signals",
         "Every signal declared in the block scene's text areas, as "
         "full declaration lines ('signal go(My_OctStr);').",
         {"type": "object", "properties": {},
          "additionalProperties": False},
         lambda args: model.list_signals())

    tool("add_connection",
         "Connect two processes with a channel, or a process to the "
         "environment with a signalroute — the block-scene connectors "
         "that carry the model's signals. out_signals are the signals "
         "sent by 'from' (declared in the block's signal-declaration "
         "text area); in_signals the ones received back.",
         {"type": "object", "properties": {
             "kind": {"type": "string", "enum": ["channel", "signalroute"],
                      "description": "channel: process to process; "
                                     "signalroute: process to env."},
             "from_id": _id_arg(),
             "to_id": {"type": "string",
                       "description": "The destination process id "
                                      "(channel). Omit for a "
                                      "signalroute (environment)."},
             "out_signals": {"type": "array", "items": {"type": "string"},
                             "description": "Signals from 'from' to the "
                                            "other end, e.g. "
                                            "['go', 'rezult']."},
             "in_signals": {"type": "array", "items": {"type": "string"},
                            "description": "Signals coming back to "
                                           "'from'."},
             "via": {"type": "array",
                     "items": {"type": "array",
                               "items": {"type": "number"},
                               "minItems": 2, "maxItems": 2},
                     "description": "Optional [[x, y], ...] waypoints "
                                    "between the two ends, in block "
                                    "scene coordinates."}},
          "required": ["kind", "from_id"], "additionalProperties": False},
         lambda args: model.add_connection(
             args["kind"], args["from_id"],
             to_id=args.get("to_id"),
             out_signals=args.get("out_signals") or (),
             in_signals=args.get("in_signals") or (),
             via=args.get("via")))

    tool("set_connection_signals",
         "Change the signal lists carried by a channel or signalroute "
         "(its labels). Each argument is a list of signal names; leave "
         "one out to keep that side as it is.",
         {"type": "object", "properties": {
             "id": _id_arg(),
             "out_signals": {"type": "array",
                             "items": {"type": "string"}},
             "in_signals": {"type": "array",
                             "items": {"type": "string"}}},
          "required": ["id"], "additionalProperties": False},
         lambda args: model.set_connection_signals(
             args["id"],
             out_signals=args.get("out_signals"),
             in_signals=args.get("in_signals")))

    tool("remove_connection",
         "Delete a channel or signalroute (the scene's undo stack, so "
         "the editor can undo it).",
         {"type": "object", "properties": {
             "id": _id_arg()},
          "required": ["id"], "additionalProperties": False},
         lambda args: model.remove_connection(args["id"]))

    tool("check_model",
         "Check the whole model: every symbol's syntax, then the full "
         "semantic parse. Returns the errors and warnings as text lines "
         "('syntax [scene] symbol: …', 'semantic …'). An empty list "
         "means the model is valid.",
         {"type": "object", "properties": {}, "additionalProperties": False},
         lambda args: model.check_model())

    tool("check_syntax",
         "Syntax-check one SDL element without touching the model: pass "
         "the grammar element name and its text. Used to validate text "
         "before adding or editing a symbol.",
         {"type": "object", "properties": {
             "element": {"type": "string", "enum": SINGLE_ELEMENTS},
             "text": {"type": "string"},
             "context": {"type": "string",
                         "description": "Process name whose variables and "
                                        "types the element is checked "
                                        "against (default: the model's "
                                        "process)."}},
          "required": ["element", "text"], "additionalProperties": False},
         lambda args: model.check_syntax(args["element"], args["text"],
                                         args.get("context", "")))

    tool("save_model",
         "Write the model back to its .pr file. Do this after "
         "modifications, so the editor (and the code generators) see "
         "them. The companion files (system_structure.pr, ASN.1) are "
         "never touched. Refuses when the file changed on disk since "
         "it was loaded (the editor saved its own edits): call "
         "reload_model to adopt the on-disk version first, or pass "
         "force: true to save anyway and discard those edits.",
         {"type": "object", "properties": {
             "force": {"type": "boolean",
                       "description": "Save even when the file changed on "
                                      "disk since it was loaded (discards "
                                      "the editor's unsaved-to-this-server "
                                      "edits). Default false."}},
          "additionalProperties": False},
         lambda args: model.save(force=bool(args.get("force"))))

    tool("reload_model",
         "Re-read the .pr files from disk, replacing the in-memory "
         "model. Use it when the editor (another process) saved its own "
         "changes: symbol ids from before the reload are invalid, so "
         "start again with list_symbols.",
         {"type": "object", "properties": {}, "additionalProperties": False},
         lambda args: model.reload_model())

    tool("model_status",
         "Quick health read: which files are loaded, whether they "
         "changed on disk since they were loaded (the editor saved "
         "them — reload_model picks that up), and the last parse "
         "errors/warnings.",
         {"type": "object", "properties": {}, "additionalProperties": False},
         lambda args: model.model_status())

    return tools


# ---------------------------------------------------------------------------
# The wire: newline-delimited JSON-RPC 2.0 on stdin/stdout.
# ---------------------------------------------------------------------------

class Server:
    def __init__(self, model, bridge=None):
        self.model = model
        # The live bridge, when a running editor answered: tool calls
        # are forwarded to it and land in the OPEN scene. Standalone
        # (no bridge): the model is this server's own copy.
        self.bridge = bridge
        self.live = bridge is not None
        catalogue = _build_tools(model)
        if self.live:
            # The implementations never run here; the catalogue is the
            # schema surface the relay forwards to the editor.
            catalogue = [{"name": t["name"],
                          "description": t["description"] + LIVE_SUFFIX,
                          "inputSchema": t["inputSchema"],
                          "_func": None}
                         for t in catalogue]
        self.tools = {t["name"]: t for t in catalogue}
        self._server_info = {
            "name": "opengeode-sdl",
            "version": "1.0",
            } if not self.live else {
            "name": "opengeode-sdl",
            "version": "1.0",
            "live": True,
        }

    # -- reading and writing ------------------------------------------------

    def _write(self, obj):
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def _reply(self, request_id, result):
        self._write({"jsonrpc": "2.0", "id": request_id, "result": result})

    def _reply_error(self, request_id, code, message):
        self._write({"jsonrpc": "2.0", "id": request_id,
                     "error": {"code": code, "message": message}})

    def serve_forever(self):
        """Read requests line by line until stdin closes. A malformed
        line is answered with a JSON-RPC parse error and the loop goes
        on: a client that sent garbage cannot take the server down."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError as exc:
                self._reply_error(None, -32700,
                                  f"parse error: {exc}")
                continue
            if not isinstance(req, dict):
                self._reply_error(None, -32600, "not a JSON-RPC request")
                continue
            method = req.get("method")
            request_id = req.get("id")
            params = req.get("params")
            if params is not None and not isinstance(params, dict):
                if method not in ("tools/call",):
                    self._reply_error(request_id, INVALID_PARAMS,
                                      "params must be an object")
                    continue
            try:
                if method == "initialize":
                    self._reply(request_id, self._initialize(params))
                elif method == "notifications/initialized":
                    pass            # a notification: no reply
                elif method == "ping":
                    self._reply(request_id, {})
                elif method == "tools/list":
                    self._reply(request_id, self._tools_list())
                elif method == "tools/call":
                    self._reply(request_id, self._tools_call(params))
                else:
                    self._reply_error(request_id, METHOD_NOT_FOUND,
                                      f"unknown method: {method}")
            except ValueError as exc:
                # A tool's argument was invalid: the model is untouched.
                self._reply_error(request_id, INVALID_PARAMS, str(exc))
            except Exception as exc:  # noqa: BLE001
                self._reply_error(request_id, INTERNAL_ERROR,
                                  f"{type(exc).__name__}: {exc}")

    # -- MCP methods --------------------------------------------------------

    def _initialize(self, params):
        return {"protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": self._server_info}

    def _tools_list(self):
        return {"tools": [
            {"name": t["name"],
             "description": t["description"],
             "inputSchema": t["inputSchema"]}
            for t in self.tools.values()]}

    def _tools_call(self, params):
        """Validate the call against the tool's schema and run it. A
        schema violation is reported as an MCP error result (isError),
        the way a client expects, rather than a JSON-RPC error.
        In live mode the call is forwarded to the running editor over
        the bridge — the tool operates on the OPEN scene."""
        if not isinstance(params, dict):
            return self._error_result("tools/call params must be an object")
        name = params.get("name")
        if not isinstance(name, str) or name not in self.tools:
            return self._error_result(f"unknown tool: {name}")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            return self._error_result("arguments must be an object")
        entry = self.tools[name]
        error = _validate_schema(entry["inputSchema"], args)
        if error:
            return self._error_result(error)
        if self.live:
            # The tool's implementation runs in the editor, against the
            # open scene: this server only forwards the (validated)
            # call and relays the result back to orbit. A dead or out-
            # of-sync connection is re-made once (the editor may have
            # been restarted); a fresh failure is reported to orbit.
            try:
                result = self._bridge_call(name, args)
            except ValueError as exc:
                return self._error_result(str(exc))
            except Exception as exc:  # noqa: BLE001
                return self._error_result(
                    f"the editor bridge failed: {type(exc).__name__}: {exc}")
        else:
            try:
                result = entry["_func"](args)
            except ValueError as exc:
                return self._error_result(str(exc))
        return {"content": [{"type": "text",
                             "text": json.dumps(result, ensure_ascii=False,
                                                indent=2)}],
                "isError": False}

    def _bridge_call(self, name, args):
        """Forward one tool call to the editor's live bridge, making
        the connection first if it broke (an editor restart, a
        desynced stream after a timeout)."""
        if self.bridge is None or not self._bridge_alive():
            client = _connect_bridge(os.environ.get(BRIDGE_ENV_VAR))
            if client is None:
                raise ValueError(
                    "the editor's live bridge is not reachable — "
                    "opengeode may have been closed; the tool cannot "
                    "run in live mode")
            self.bridge = client
        return self.bridge.call("tools/call",
                                {"name": name, "arguments": args})

    def _bridge_alive(self):
        try:
            self.bridge.call("ping")
            return True
        except Exception:  # noqa: BLE001
            return False

    def _error_result(self, message):
        return {"content": [{"type": "text", "text": message}],
                "isError": True}


def _validate_schema(schema, args):
    """Check args against the tool's JSON Schema — the subset the tool
    schemas use (object, string, number, integer, boolean, array, enum,
    required, min/max, additionalProperties). Returns None when valid,
    else the first problem as text. No JSON pointer gymnastics: a clear
    message beats a formal one."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    props = schema.get("properties", {})
    for key, value in args.items():
        if key not in props:
            if schema.get("additionalProperties") is False:
                return f"unknown argument: {key}"
            continue
        problem = _validate_value(props[key], value, key)
        if problem:
            return problem
    for key in schema.get("required", []):
        if key not in args:
            return f"missing argument: {key}"
    return None


def _validate_value(spec, value, name):
    kind = spec.get("type")
    if kind == "string" and not isinstance(value, str):
        return f"{name} must be a string"
    if kind == "number" and not isinstance(value, (int, float)):
        return f"{name} must be a number"
    if kind == "integer" and not (isinstance(value, int)
                                 and not isinstance(value, bool)):
        return f"{name} must be an integer"
    if kind == "boolean" and not isinstance(value, bool):
        return f"{name} must be a boolean"
    if kind == "array":
        if not isinstance(value, list):
            return f"{name} must be an array"
        if "minItems" in spec and len(value) < spec["minItems"]:
            return f"{name} needs at least {spec['minItems']} items"
        if "maxItems" in spec and len(value) > spec["maxItems"]:
            return f"{name} takes at most {spec['maxItems']} items"
        for item in value:
            problem = _validate_value(spec.get("items", {}), item, name)
            if problem:
                return problem
    if "enum" in spec and value not in spec["enum"]:
        return f"{name} must be one of {spec['enum']}"
    if "minimum" in spec and isinstance(value, (int, float)) \
            and value < spec["minimum"]:
        return f"{name} must be >= {spec['minimum']}"
    if "maximum" in spec and isinstance(value, (int, float)) \
            and value > spec["maximum"]:
        return f"{name} must be <= {spec['maximum']}"
    return None


def main():
    # The model's .pr files come from the command line; without them the
    # server has nothing to control. Orbit starts it in the project
    # directory, so a bare '*.pr' works there too.
    import glob
    argv = sys.argv[1:]
    if len(argv) == 1 and "*" in argv[0]:
        argv = sorted(glob.glob(os.path.join(os.getcwd(), argv[0])))
    if not argv:
        argv = sorted(glob.glob(os.path.join(os.getcwd(), "*.pr")))
    # A running editor exports its bridge socket: when it is there and
    # answers, every tool call is forwarded to the LIVE model — orbit's
    # edits appear in the open scene immediately. Without it, the
    # server controls its own copy of the files on disk (standalone).
    bridge = _connect_bridge(os.environ.get(BRIDGE_ENV_VAR))
    model = None
    if bridge is None:
        try:
            model = SdlModel(argv)
        except ValueError as exc:
            sys.stderr.write(f"opengeode-sdl: {exc}\n")
            sys.exit(1)
    server = Server(model, bridge=bridge)
    server.serve_forever()


#: The env var the editor sets to point at its live bridge socket.
BRIDGE_ENV_VAR = "OPENGEODE_SDL_BRIDGE"

#: How long to wait for the bridge to answer a request, seconds.
BRIDGE_TIMEOUT = 20.0

#: How many stale replies (left over after a timeout) to drain before
#: giving up on a desynced bridge connection.
_MAX_STALE_BRIDGE_REPLIES = 64


class _BridgeClient:
    """The relay's end: a synchronous client to the editor's live
    bridge. The wire is the same newline-delimited JSON-RPC the server
    itself speaks — one request per line, one reply per line."""

    def __init__(self, path, timeout=BRIDGE_TIMEOUT):
        import socket
        self.path = path
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect(path)
        self._file = self.sock.makefile("rwb")

    def call(self, method, params=None):
        """One JSON-RPC request/reply. The reply's id must match the
        request — a late reply left over after a timeout is discarded,
        never misread as this call's answer. Returns the result, or
        raises ValueError with the message the bridge sent."""
        req_id = next(self._ids)
        req = {"jsonrpc": "2.0", "id": req_id, "method": method,
               "params": params or {}}
        self._file.write((json.dumps(req) + "\n").encode("utf-8"))
        self._file.flush()
        # Drain at most a few stale replies (each a line that answered
        # an earlier, timed-out request) before this one arrives.
        for _ in range(_MAX_STALE_BRIDGE_REPLIES):
            line = self._file.readline()
            if not line:
                raise ValueError("the editor closed the bridge connection")
            reply = json.loads(line.decode("utf-8"))
            if reply.get("id") == req_id:
                break
        else:
            raise ValueError(
                "the editor bridge is out of sync (no reply matched "
                f"request {req_id}); reconnecting is required")
        if "error" in reply:
            raise ValueError(reply["error"].get("message", "bridge error"))
        return reply.get("result")

    _ids = iter(range(1, 2 ** 30))

    def close(self):
        try:
            self._file.close()
            self.sock.close()
        except Exception:
            pass


def _connect_bridge(path, ping_timeout=2.0):
    """Connect to the editor's live bridge when the path names a live
    socket, and verify it answers. Returns the client, or None — a
    missing or dead bridge must not break the standalone server.
    The 2-second bound applies to the PING only: the returned client
    keeps the full BRIDGE_TIMEOUT for the session, so a slow tool call
    (a big check_model, a save) is not cut off mid-flight."""
    if not path:
        return None
    try:
        client = _BridgeClient(path, timeout=ping_timeout)
        client.call("ping")
        # Verified alive: give the session the full timeout.
        client.timeout = BRIDGE_TIMEOUT
        client.sock.settimeout(BRIDGE_TIMEOUT)
        return client
    except Exception:
        return None


if __name__ == "__main__":
    main()
