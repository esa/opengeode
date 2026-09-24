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
    "state":             (sdlSymbols.State, False),
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

    # -- loading and scenes -------------------------------------------------

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
        self.block = block
        scene = SDL_Scene(context="block")
        scene.render_everything(block)
        self.scene = scene

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
        if needs_parent and parent is None:
            raise ValueError(f"{kind} needs a parent symbol")
        if not needs_parent and parent is not None:
            raise ValueError(f"{kind} is a floating symbol; "
                             "it cannot take a parent")
        # The class' own follower rules are the authority on placement:
        # they mirror what the editor's toolbar allows.
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
        elif cls in (sdlSymbols.State, sdlSymbols.Procedure):
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
        return [e.msg for e in errs], [w.msg for w in warnings]

    def _main_file(self):
        """The .pr file the block scene is saved to: the one whose name
        matches the block (the GUI's convention), else the first file."""
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
        self._cwd = os.getcwd()
        os.chdir(self.model_dir)
        try:
            _, syntax_errors, semantic_errors, warnings, _ = \
                ogParser.parseSingleElement(elem=element, string=text,
                                            context=self._context(context))
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

    def save(self):
        """Write the model back to the .pr file(s), mirroring the GUI's
        save_diagram: translate to a non-negative coordinate origin,
        serialise, and write. The editor reloads the file on its own."""
        scene = self.scene
        # Coordinates must be non-negative for a clean reload
        scene.translate_to_origin()
        pr_raw = Pr.parse_scene(scene, full_model=self._full_model())
        pr_data = "\n".join(pr_raw)
        # The GUI writes the process file; the system structure, when
        # there is one, is read-only and untouched.
        target = self._main_file()
        with open(target, "w", encoding="utf-8") as f:
            f.write(pr_data)
        return {"saved": os.path.basename(target), "bytes": len(pr_data)}


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
         "never touched.",
         {"type": "object", "properties": {}, "additionalProperties": False},
         lambda args: model.save())

    return tools


# ---------------------------------------------------------------------------
# The wire: newline-delimited JSON-RPC 2.0 on stdin/stdout.
# ---------------------------------------------------------------------------

class Server:
    def __init__(self, model):
        self.model = model
        self.tools = {t["name"]: t for t in _build_tools(model)}
        self._server_info = {
            "name": "opengeode-sdl",
            "version": "1.0",
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
        the way a client expects, rather than a JSON-RPC error."""
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
        try:
            result = entry["_func"](args)
        except ValueError as exc:
            return self._error_result(str(exc))
        return {"content": [{"type": "text",
                             "text": json.dumps(result, ensure_ascii=False,
                                                indent=2)}],
                "isError": False}

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
    try:
        model = SdlModel(argv)
    except ValueError as exc:
        sys.stderr.write(f"opengeode-sdl: {exc}\n")
        sys.exit(1)
    server = Server(model)
    server.serve_forever()


if __name__ == "__main__":
    main()
