#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''The live bridge: MCP tool calls run INSIDE the running editor.

The headless server (SdlMcpServer) owns its own copy of the model —
orbit's edits landed on disk, and the editor reloaded from there. This
module closes that gap: the editor hosts the SAME tool implementations
against its LIVE scenes, behind a user-only QLocalServer. The MCP
server orbit starts detects the bridge, connects, and forwards every
tool call to the running instance — an orbit-side ``add_symbol`` lands
in the open scene immediately, visible and undoable.

Wire (both ends newline-delimited JSON-RPC 2.0):

    orbit ──stdio── SdlMcpServer ──unix socket── OrbitMcpBridge (editor)

The socket name is deterministic so both sides agree without a
handshake file: ``opengeode-sdl-<pid>.sock`` in the runtime directory,
where <pid> is the EDITOR's process id — the bridge announces it by
setting OPENGEODE_SDL_BRIDGE in the environment the panel gives the
conversation, which orbit passes to the MCP server it spawns.

Threading: tool calls arrive on a Qt socket in the GUI thread and run
synchronously there — no races with the editor's own actions. The
headless ``SdlModel`` code is reused unchanged for the scenes API; the
live model subclass only overrides what differs: the scene entry
point (the view's live block scene), saving (the view's own
save_diagram), and staleness (the view is the source of truth).

Security: the socket is created with UserAccessOption (0o700) and
lives in the user's runtime directory — another user on the machine
cannot connect, and the tool surface is the validated MCP schema
(SdlMcpServer._validate_schema) applied before dispatch.
'''

import json
import os
import sys

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from . import ogParser, sdlSymbols, undoCommands
from .SdlMcpServer import SdlModel, SINGLE_ELEMENTS, SYMBOL_KINDS, _kind_of

# ---------------------------------------------------------------------------
# The live model: the same tools, the editor's live scenes.
# ---------------------------------------------------------------------------


class LiveSdlModel(SdlModel):
    '''SdlModel over the EDITOR's live scenes: the scene entry point is
    the view's block scene, saves go through the view's own
    save_diagram (so the editor's monitor and title bar update), and
    staleness is meaningless — the live scene IS the source of truth.'''

    def __init__(self, view, main_window):
        # Deliberately NOT calling SdlModel.__init__ — it parses the
        # .pr files and renders its own scene. The editor already did
        # that: the view's scene is the model. (The SdlModel instance
        # attributes the tools rely on are set up below.)
        self.view = view
        self.main_window = main_window
        # SdlModel attributes the tool implementations use:
        self._symbol_ids = {}
        self._scene_names = {}
        self.ast = getattr(view, 'ast', None)
        self.parse_errors = []
        self.parse_warnings = []
        # The view is the source of truth: no mtime snapshot to keep.
        self._mtimes = {}

    # -- the view's state, resolved at call time -----------------------------
    # The bridge can exist before any model is opened (the conversation
    # starts with the editor), so nothing about the files is captured:
    # these read the view as it is when a tool runs.

    @property
    def pr_files(self):
        '''The files the editor has open: its current file plus the
        read-only companions it was loaded with.'''
        files = set(getattr(self.view, 'readonly_pr', None) or set())
        fname = getattr(self.view, 'filename', None)
        if fname:
            files.add(fname)
        return sorted(os.path.abspath(p) for p in files)

    @property
    def model_dir(self):
        files = self.pr_files
        return os.path.dirname(files[0]) if files else os.getcwd()

    def _live_files(self):
        return self.pr_files

    # -- what the view replaces ---------------------------------------------

    @property
    def scene(self):
        '''The live block scene of the editor (the root of the model).'''
        return self.view.top_scene()

    @scene.setter
    def scene(self, value):
        '''Ignored: the live scene is not replaceable from a tool call
        (the headless reload() assigns self.scene; the live model never
        runs it — the view owns the scene lifecycle).'''
        pass

    def _main_file(self):
        '''The file the editor saves to: the view's filename.'''
        return getattr(self.view, 'filename', None) or (
            self.pr_files[0] if self.pr_files else '')

    def _full_model(self):
        '''True when the editor's model is a single .pr file (no
        companion system structure): the same convention the headless
        server uses.'''
        return len(self.pr_files) == 1

    def save(self, force=False):
        '''Save through the editor's own action, so the monitor's
        timestamps and the window title update exactly as a manual
        save does. Runs on the GUI thread (the bridge guarantees it).'''
        del force    # the live scene IS the current model: no stale copy
        # The GUI's own save: same code path as Ctrl+S (it translates
        # coordinates to a non-negative origin itself), so the file
        # monitor and the window title update exactly as a manual save.
        success = self.view.save_diagram()
        if success is False:
            raise ValueError("the editor could not save the diagram")
        return {"saved": os.path.basename(self._main_file()),
                "bytes": os.path.getsize(self._main_file())}

    def reload_model(self):
        '''Reload the editor's model from disk, the editor's own way:
        the view re-loads the file. A broken file leaves the previous
        model (atomic, like the headless reload).'''
        fname = self._main_file()
        if not fname or not os.path.isfile(fname):
            raise ValueError(f"no model file to reload: {fname}")
        success = self.view.load_file([fname], is_reload=True)
        if not success:
            raise ValueError("the model could not be reloaded from disk "
                             "(the editor kept the current one)")
        self._symbol_ids = {}
        self._scene_names = {}
        self.pr_files = self._live_files()
        return {"reloaded": [os.path.basename(p) for p in self.pr_files]}

    def model_status(self):
        '''The live bridge has no stale copy — the scene is the model.
        Reports the editor's own unsaved state instead.'''
        clean = self.view.is_model_clean()
        return {"files": [os.path.basename(p) for p in self.pr_files],
                "saved_to": os.path.basename(self._main_file())
                            if self._main_file() else "",
                "external_changes": [],
                "stale": False,
                "unsaved": not clean,
                "live": True,
                "parse_errors": [],
                "parse_warnings": []}

    def add(self, kind, scene_name=None, parent_id=None, text=None,
            x=None, y=None):
        '''Insert a symbol in the LIVE scene, through its undo stack —
        the editor can undo it with Ctrl+Z, exactly like its own
        toolbar insertions. Mirrors the headless add()'s placement rules
        (follower checks, decision answers, sub-scenes) but routes the
        insertion through InsertSymbol instead of touching the scene
        directly, and never enters text-edit mode (a remote edit must
        not steal the user's keyboard focus).'''
        from PySide6.QtCore import QPointF
        if kind not in SYMBOL_KINDS:
            raise ValueError(f"unknown symbol kind: {kind}")
        cls, needs_parent = SYMBOL_KINDS[kind]
        parent = None
        if parent_id is not None:
            parent_scene, parent = self.symbol_by_handle(parent_id)
            scene = parent_scene
        else:
            scene = self.scene_named(scene_name)
        if needs_parent is True and parent is None:
            raise ValueError(f"{kind} needs a parent symbol")
        if needs_parent is False and parent is not None:
            raise ValueError(f"{kind} is a floating symbol; "
                             "it cannot take a parent")
        # The class' own follower rules are the authority on placement
        # (they mirror the editor's toolbar); a NEXTSTATE (parented
        # state) follows only a chain's LAST symbol.
        if parent is not None:
            allowed = parent.allowed_followers
            if cls.__name__ not in allowed and cls not in allowed:
                if not any(cls.__name__ == a for a in allowed) \
                        and not any(isinstance(a, str) and
                                    cls.__name__ == a for a in allowed):
                    raise ValueError(
                        f"{_kind_of(parent)} cannot be followed by {kind}")
        pos = QPointF(x, y) if (x is not None and y is not None) else None
        item = cls()
        if item not in scene.items():
            scene.addItem(item)
        # The editor's own insertion path: undoable, keeps the scene
        # bookkeeping (grabbers, connections) consistent with a manual
        # insertion.
        scene.undo_stack.push(undoCommands.InsertSymbol(
            item=item, parent=parent, pos=pos))
        if parent is None:
            from .opengeode import G_SYMBOLS
            G_SYMBOLS.add(item)
        if cls is sdlSymbols.Decision:
            for _ in range(2):
                self.add("decision_answer", parent_id=str(id(item)),
                         text="answer")
        elif cls is sdlSymbols.Procedure or cls is sdlSymbols.Process \
                or (cls is sdlSymbols.State and parent is None):
            # Containers get their sub-scene (the editor's place_symbol
            # convention); a PARENTED State is the NEXTSTATE terminator
            # — no sub-scene.
            item.nested_scene = scene.create_subscene(
                    cls.__name__.lower(), scene)
            item.nested_scene.name = str(item)
        if text is not None and getattr(item, "has_text_area", True):
            item.text.setPlainText(text)
            item.ast.inputString = text
            item.text.try_resize()
        scene.scene_refresh()
        return self._symbol_info(item, scene)

    def check_syntax(self, element, text, context=""):
        '''check_syntax on the live model: same parser, the editor's
        process context. The chdir dance is the headless one's — the
        parser resolves the ASN.1 view relative to the CWD.'''
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

    # The headless implementation is reused verbatim (scenes(),
    # symbols(), find(), add(), remove(), set_text(), move(),
    # check_model(), _semantic_check(), _symbol_info(),
    # symbol_by_handle(), scene_named(), _context()): they only touch
    # self.scene, which here is the live block scene.


# ---------------------------------------------------------------------------
# The socket bridge
# ---------------------------------------------------------------------------


def bridge_socket_name(pid):
    '''The deterministic socket name both ends agree on.'''
    runtime = os.environ.get('XDG_RUNTIME_DIR') or '/tmp'
    return os.path.join(runtime, f'opengeode-sdl-{pid}.sock')

class OrbitMcpBridge(QObject):
    '''A QLocalServer in the editor that speaks the MCP tools/call
    protocol to the SdlMcpServer relay. Every request runs a tool
    implementation against the LIVE scene, synchronously, on the GUI
    thread.'''

    # A short human-readable line for the editor's message window.
    connected = Signal(str)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.view = main_window.view
        self.server = QLocalServer()
        # User-only: another user on the machine cannot connect.
        self.server.setSocketOptions(QLocalServer.SocketOption
                                     .UserAccessOption)
        self.model = LiveSdlModel(self.view, main_window)
        name = bridge_socket_name(os.getpid())
        # A previous run of this pid may have left the file behind.
        QLocalServer.removeServer(name)
        if not self.server.listen(name):
            raise RuntimeError(f"bridge cannot listen on {name}: "
                                f"{self.server.errorString()}")
        self.socket_path = self.server.fullServerName()
        self._conns = []
        self.server.newConnection.connect(self._on_new_connection)
        # The environment the chat panel passes to the conversation:
        # orbit forwards it to the MCP server, which finds the bridge.
        self.env_var = 'OPENGEODE_SDL_BRIDGE'
        self.env_value = self.socket_path

    def close(self):
        '''Tear the bridge down with the editor.'''
        try:
            self.server.close()
        except Exception:
            pass
        for conn in list(self._conns):
            try:
                conn.disconnectFromServer()
            except Exception:
                pass
        self._conns = []

    # -- connections and requests ------------------------------------------

    @Slot()
    def _on_new_connection(self):
        while self.server.hasPendingConnections():
            conn = self.server.nextPendingConnection()
            self._conns.append(conn)
            conn.readyRead.connect(lambda c=conn: self._on_ready_read(c))
            conn.disconnected.connect(lambda c=conn: self._on_gone(c))
            self.connected.emit(self.socket_path)

    def _on_gone(self, conn):
        if conn in self._conns:
            self._conns.remove(conn)

    def _on_ready_read(self, conn):
        '''Read one newline-delimited JSON-RPC request, run the tool,
        reply. Runs on the GUI thread — the tool operates on the live
        scene with no risk of tearing it mid-render.'''
        if conn.state() != QLocalSocket.LocalSocketState.ConnectedState:
            return
        data = bytes(conn.readAll())
        for line in [ln for ln in data.decode('utf-8', 'replace').split('\n')
                     if ln.strip()]:
            request_id = None
            try:
                req = json.loads(line)
                request_id = req.get('id')
                result = self._dispatch(req)
            except json.JSONDecodeError as exc:
                self._reply(conn, None, error=f"parse error: {exc}")
                continue
            except ValueError as exc:
                # A tool's argument was invalid: the live model is
                # untouched — same contract as the headless server.
                self._reply(conn, request_id, error=str(exc))
                continue
            except Exception as exc:  # noqa: BLE001
                self._reply(conn, request_id,
                            error=f"{type(exc).__name__}: {exc}")
                continue
            self._reply(conn, request_id, result=result)

    def _dispatch(self, req):
        '''The relay protocol: tools/list (so the relay can verify the
        live surface matches) and tools/call. The tool catalogue is the
        headless one — same names, same schemas — bound to the live
        model.'''
        if not isinstance(req, dict):
            raise ValueError("not a JSON-RPC request")
        method = req.get('method')
        params = req.get('params') or {}
        if method == 'ping':
            return {}
        if method == 'tools/list':
            from .SdlMcpServer import _build_tools
            return {"tools": [{"name": t["name"],
                               "description": t["description"],
                               "inputSchema": t["inputSchema"]}
                              for t in _build_tools(self.model)]}
        if method == 'tools/call':
            name = params.get('name')
            args = params.get('arguments') or {}
            from .SdlMcpServer import _build_tools, _validate_schema
            tools = {t['name']: t for t in _build_tools(self.model)}
            if not isinstance(name, str) or name not in tools:
                raise ValueError(f"unknown tool: {name}")
            error = _validate_schema(tools[name]['inputSchema'], args)
            if error:
                raise ValueError(error)
            return tools[name]['_func'](args)
        raise ValueError(f"unknown method: {method}")

    def _reply(self, conn, request_id, result=None, error=None):
        if error is not None and error is not False:
            payload = {"jsonrpc": "2.0", "id": request_id,
                       "error": {"code": -32602, "message": error}}
        else:
            payload = {"jsonrpc": "2.0", "id": request_id,
                       "result": result}
        conn.write((json.dumps(payload, ensure_ascii=False) + "\n")
                   .encode('utf-8'))
        conn.flush()


def attach(main_window):
    '''Create the bridge for a main window, or None when it cannot
    (QtNetwork missing, say). The env hint is exported to the process
    environment so the chat panel's conversation inherits it.'''
    try:
        bridge = OrbitMcpBridge(main_window)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"orbit bridge disabled: {exc}\n")
        return None
    os.environ[bridge.env_var] = bridge.env_value
    return bridge
