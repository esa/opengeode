---
name: sdl-mcp-remote-control
description: >
  Reference for driving an OpenGEODE SDL model remotely through the
  opengeode-sdl MCP server: the seventeen tools, their arguments, the
  symbol kinds, scenes, connections (channels/signalroutes), signal
  declarations, the safe editing procedure (check before saving), and
  the error formats to expect.
---

# OpenGEODE SDL Remote Control (MCP) — Skill Documentation

> **Purpose**: You have access to an MCP tool server named
> **`opengeode-sdl`** that edits the SDL model of the current project
> directly. Its tools appear as `mcp__opengeode-sdl__<tool>`. This
> document tells you what each tool does, the exact argument shapes,
> and the operating procedure for editing a model safely. The general
> SDL language knowledge is in the `sdl-model-construction` skill; this
> one covers only the remote-control interface.

## 1. How the server works

**Live mode (the usual case).** When OpenGEODE's editor is running
with the model open, the server relays every tool call to it over a
local socket: the tools operate on the **model currently displayed in
the editor** — an `add_symbol` appears in the open diagram
immediately, is undoable there (Ctrl+Z), and `save_model` uses the
editor's own save action. You are editing the user's live session.
Consequences: call `model_status` when unsure which model is current;
do not edit the `.pr` files on disk yourself (the editor owns them in
live mode); a symbol the user deletes in the editor is gone — its id
fails with "symbol is gone", so re-list before acting.

**Standalone mode (fallback).** Without a running editor the server
parses the `.pr` files itself and holds its own copy.
**Modifications are in memory until you call `save_model`**; the
editor picks the change up from disk through its file monitor, and
the code generators read the same files. The save refuses when the
file changed on disk since it was loaded (see `save_model`).

Scenes: a model has a **block** scene (the processes), a **process**
scene per process (its START, states, text areas, procedures), and a
nested **state**/**procedure** scene for each state or procedure that
has content. Scene names are reported by `list_symbols`; the common
forms are:

- `"block"` — the top scene (process boxes)
- `"process og"` — the process named `og`
- `"process og state wait"` — a nested state's scene

A scene argument also accepts the bare last word (`"og"`, `"wait"`)
when it is unambiguous.

Symbols are addressed by **id strings** (`"1402345..."`) returned by
`list_symbols` / `find_symbol` / `add_symbol`. In standalone mode ids
are stable for the server's lifetime; in live mode the user's own
editor actions (undo, delete, reload) can invalidate them — a gone
symbol's id is reported as such, so re-list after user actions.

## 2. The tools

### list_symbols
Enumerate one scene. Returns each symbol's `id`, `kind`, `text`,
`scene`, position `x`/`y`, `parent_id` (if attached), `children` (one
level), and `nested_scene` (for states/procedures/processes).
```
{"scene": "process og"}
```

### find_symbol
Locate symbols: filter by `kind`, by `text_contains` (substring,
case-insensitive), or by `near: [x, y]` (results sorted by distance).
Returns at most `max_results` (default 50). Without filters, returns
the scene's symbols like `list_symbols`.
```
{"scene": "process og", "kind": "task", "text_contains": "counter"}
```

### get_symbol
One symbol's full detail (same fields as list_symbols, plus children).
```
{"id": "140234567890"}
```

### add_symbol
Insert a symbol. Two placements:

- **Attached** — pass `parent_id`: the symbol is inserted below the
  parent (vertical chain: task, output, decision, procedure_call,
  create, join, stops) or as a branch under it (horizontal: input,
  connect, continuous_signal, decision_answer under a decision). The
  parent's own follower rules decide, exactly as the editor's toolbar
  does; an impossible placement is reported, never coerced.
- **Floating** — no `parent_id`: the symbol is placed at `x`, `y` in
  `scene` (floating labels, text areas, states, procedures, starts).

`text` is the symbol's SDL content (e.g. `"x := x + 1"` for a task).
A `decision` automatically gets two `decision_answer` children; a
floating `state`, a `procedure` or a `process` opens a nested scene
for its content.

**Creating a new process** (in the block view):

```
{"kind": "process", "scene": "block", "x": 900, "y": 400, "text": "second"}
→ returns nested_scene: "process second"
{"kind": "start", "scene": "process second", "x": 100, "y": 100}
{"kind": "task", "parent_id": "<start id>", "text": "counter := 0"}
{"kind": "state", "parent_id": "<task id>", "text": "idle"}
```

**NEXTSTATE — ending a transition with a state.** A `state` is
**dual-role**: floating it is a state box (with its own sub-scene to
build its content); attached with `parent_id` it is the **NEXTSTATE
terminator** of that transition. It is accepted only after the chain's
**last** symbol (task, output, decision branch, join…): the same rule
as the editor's toolbar. Mid-chain it is rejected — do not fight the
error: the chain's end is the symbol with no `children` of its own
(inspect with `get_symbol`, or add to the deepest symbol you placed).
```
{"kind": "state", "parent_id": "<last task id>", "text": "Running"}
```

### remove_symbol
Delete a symbol. Deleting a **state**, **procedure** or **process**
removes its whole sub-diagram, so those require `"force": true` — a
guard against one call erasing a diagram by accident.
```
{"id": "<id>"}
{"id": "<state id>", "force": true}
```

### set_symbol_text
Change a symbol's SDL text. Apply, then check: call `check_model` (or
`check_syntax`) to validate before saving.
```
{"id": "<id>", "text": "counter := counter + 1"}
```

### move_symbol
Move a symbol to absolute scene coordinates.
```
{"id": "<id>", "x": 1200, "y": 800}
```

### add_connection
Connect two processes with a **channel**, or one process to the
environment with a **signalroute** — the block-scene connectors that
carry the model's signals. The signals must already be declared (see
`add_signal_declaration`); use `list_signals` to see what exists.

- `kind: "channel"` — process to process: `from_id` and `to_id` are
  the two **process** symbols in the block scene.
- `kind: "signalroute"` — process to the environment: only `from_id`;
  no `to_id`.
- `out_signals` — signal names sent by `from_id` (e.g. `["go"]`);
  `in_signals` — the ones it receives back (e.g. `["rezult"]`).
- `via` — optional `[[x, y], ...]` waypoints to shape the line.

The connection is returned with its `id`; it appears in the process'
`connections` in `list_symbols` (with `from_id`, `to_id`, the signal
lists). Deleting is `remove_connection`.
```
{"kind": "channel", "from_id": "<og id>", "to_id": "<second id>",
 "out_signals": ["go"], "in_signals": ["rezult"]}
{"kind": "signalroute", "from_id": "<og id>", "out_signals": ["rezult"]}
```

### set_connection_signals
Change the signal lists of an existing connection. Each argument is a
list of signal names; leave one out to keep that side untouched.
```
{"id": "<connection id>", "out_signals": ["go", "ping"]}
```

### remove_connection
Delete a channel or signalroute (undoable).
```
{"id": "<connection id>"}
```

### add_signal_declaration
Declare a signal in the block scene (its signal-declaration text
area): `signal <name>` or `signal <name>(<param_type>)`. The
`param_type` is an ASN.1 type name from the data view. Declare the
signals **before** creating connections that carry them.
```
{"signal": "go", "param_type": "My_OctStr"}
{"signal": "ping"}
```

### list_signals
Every signal declared in the block scene, as full declaration lines
(`signal go(My_OctStr);`).
```
{}
```

### check_model
Check the whole model: every symbol's syntax, then the full semantic
parse. Result: `status` ("Done"/"Errors"), `errors` and `warnings` as
text lines, and their counts. **Run this before every save.**
```
{}
```

### check_syntax
Syntax-check one SDL element *without touching the model* — to
validate a text before adding or editing a symbol. `element` is the
parser's grammar name; the common ones: `task`, `output`,
`procedure_call`, `decision`, `input_part`, `label`, `text_area`,
`create_request`, `terminator_statement` (a nextstate/stop/join).
`context` (optional) names the process whose variables and types the
element is checked against.
```
{"element": "task", "text": "counter := counter + 1"}
```

### save_model
Write the model back to the main `.pr` file. The companion files
(system_structure.pr, the ASN.1 data view) are never touched. Do it
after modifications, after `check_model` reports no errors.
```
{}                      # refuses if the file changed on disk (see below)
{"force": true}         # save anyway, discarding those on-disk changes
```

In **standalone mode** the editor is a separate process saving the
same file: if it changed on disk since it was loaded here, a plain
`save_model` **refuses** rather than clobber it — the error names the
files. Then either call `reload_model` to adopt the editor's version
(your unsaved changes here are lost, so `save_model` first if you
have any), or pass `force: true` to keep this server's version. In
**live mode** none of this applies: the save goes through the
editor's own action and there is no stale copy by construction.

### reload_model
Re-read the `.pr` files from disk, replacing everything in memory.
Call it when the editor saved its own changes (a save that refused
told you, or `model_status` shows `stale: true`), or to discard your
own in-memory modifications. **All symbol ids from before the reload
are invalid** — start again with `list_symbols`.

### model_status
What is loaded, whether the files changed on disk since (`stale`,
`external_changes` — the editor's saves), and the last parse
errors/warnings. In live mode it also reports `live: true` and
`unsaved` (the editor's own unsaved-edits state). Cheap; call it when
unsure which side is current.

## 3. Symbol kinds

```
input, connect, output, decision, alternative, decision_answer,
join, procedure_stop, process_stop, label, task, procedure_call,
create, text, state, procedure, process, process_type, start,
procedure_start, state_start, continuous_signal
```

- `task`, `output`, `procedure_call`, `create`, `join`,
  `procedure_stop`, `process_stop`, `decision`, `alternative` —
  vertical: chained below a parent
- `input`, `connect`, `continuous_signal`, `decision_answer` —
  horizontal: branched under a state/decision
- `label`, `text`, `state`, `procedure`, `process`, `process_type`,
  `start`, `procedure_start`, `state_start` — floating — **and `state`
  is also attachable**: parented it is the NEXTSTATE terminator (see
  add_symbol); `process` is added in the **block** scene

## 4. Operating procedure

1. **Read before writing.** `list_symbols` (or `find_symbol`) on the
   scene you are about to change. Ids come from these calls only.
2. **Validate text first.** For a new statement, `check_syntax` with
   the element name; fix errors before it enters the model.
3. **Edit**: `add_symbol` / `set_symbol_text` / `move_symbol` /
   `remove_symbol`. One structural change at a time.
4. **Check**: `check_model`. Fix reported errors (`set_symbol_text`,
   `remove_symbol`) and check again.
   **Structural order matters**: declare signals
   (`add_signal_declaration`) before wiring connections
   (`add_connection`); create a process before its nested scene can be
   addressed; end every transition with an attached `state`
   (NEXTSTATE) or a stop/join — a transition that ends nowhere is a
   semantic error (`check_model` reports it).
5. **Save**: `save_model`. Only then are the `.pr` files updated.
   In standalone mode a refusal means the editor saved the file
   meanwhile: decide which version wins — `reload_model` (editor
   wins) or `force: true` (this server's model wins) — then save.
6. **Re-read** after saving if further work needs fresh ids
   (`save_model` re-renders; ids of surviving symbols stay valid).
7. **The user edits too.** In live mode their editor actions (undo,
   delete, reload) can invalidate ids — re-list before acting after
   they report doing something. In standalone mode, when they say
   they saved the model, `model_status` shows `stale`: `reload_model`
   before anything else.

Error lines carry their origin: `syntax [scene] <symbol>: …` for a
symbol's syntax, `semantic …` for the model parse. A tool call that
fails returns `isError` with the reason as text — read it, fix the
cause, do not retry blindly.

## 5. Worked examples

Add a counter task to a process's START transition:

```
1. mcp__opengeode-sdl__find_symbol
   {"scene": "process og", "kind": "start"}
   → symbols: [{id: "943681234", kind: "start", ...}]

2. mcp__opengeode-sdl__check_syntax
   {"element": "task", "text": "counter := 0"}
   → syntax_errors: []

3. mcp__opengeode-sdl__add_symbol
   {"kind": "task", "parent_id": "943681234", "text": "counter := 0"}
   → {id: "943689900", kind: "task", text: "counter := 0", ...}

4. mcp__opengeode-sdl__check_model   {}  → status: "Done"

5. mcp__opengeode-sdl__save_model    {}  → {saved: "og.pr", ...}
```

**Build a complete new process** in the block view, wire it, and save —
the full structural flow:

```
1. add_symbol   {"kind": "process", "scene": "block", "x": 900,
                 "y": 400, "text": "second"}
   → nested_scene: "process second"

2. add_symbol   {"kind": "start", "scene": "process second",
                 "x": 100, "y": 100}

3. add_symbol   {"kind": "task", "parent_id": "<start id>",
                 "text": "counter := 0"}

4. add_symbol   {"kind": "state", "parent_id": "<task id>",
                 "text": "idle"}          # the NEXTSTATE terminator

5. add_symbol   {"kind": "state", "scene": "process second",
                 "x": 400, "y": 300, "text": "idle"}
                 # the STATE BOX the NEXTSTATE refers to — it must
                 # exist; its content is built by attaching inputs
                 # under it (next step)
5b. add_symbol  {"kind": "input", "parent_id": "<state box id>",
                 "text": "go"}        # a transition of state idle

6. add_signal_declaration
                 {"signal": "tick"}       # before wiring connections

7. add_connection
                 {"kind": "channel", "from_id": "<og id>",
                  "to_id": "<second id>", "out_signals": ["go"],
                  "in_signals": ["rezult"]}

8. check_model  {}   → fix anything reported

9. save_model   {}   → {saved: "second.pr, og.pr, system_structure.pr"}
```

Notes on that flow:
- A process' **state machine** is built in its nested scene: floating
  `state` boxes (one per state — the target of each NEXTSTATE), then
  `input` symbols branched under a box, then the transition chain
  below the input, ending with an attached `state` (NEXTSTATE) whose
  text names one of the boxes.
- When the block scene holds **more than one process definition**, the
  save writes each process to its own `.pr` file (`second.pr`) and
  regenerates the system structure with `REFERENCED` processes — the
  TASTE convention. `save_model`'s result names every file written.
- To give the new process its **own interface with the environment**,
  add a `signalroute` (`{"kind": "signalroute", "from_id":
  "<second id>", "out_signals": ["tick"]}`) — the serializer turns it
  into a channel + route pair in the structure.

Then to attach an input to a state and add it to the flow:

```
1. find_symbol  {"scene": "process og", "kind": "state",
                 "text_contains": "Ready"}
2. add_symbol   {"kind": "input", "parent_id": "<state id>",
                 "text": "go"}
3. add_symbol   {"kind": "task", "parent_id": "<input id>",
                 "text": "counter := counter + 1"}
4. add_symbol   {"kind": "state", "parent_id": "<task id>",
                 "text": "Running"}        # NEXTSTATE
5. check_model → fix anything reported → save_model
```

## 6. Limits and conventions

- The server holds **one model**, the files it was started with.
  Tool arguments never carry file paths: there is nothing to point at
  another file.
- Ids are opaque; do not invent them or assume a pattern.
- `check_model`'s `warnings` are advisory (e.g. "expression is always
  true"); errors must be fixed before saving.
- The ASN.1 data view is outside the server's scope (types are
  validated against it); the **system structure is not**: signal
  declarations, channels and signalroutes are part of the model, and a
  multi-process save regenerates the structure file.
- If a tool reports the model as stale or a symbol as gone, re-read
  with `list_symbols` and continue from the fresh ids.
