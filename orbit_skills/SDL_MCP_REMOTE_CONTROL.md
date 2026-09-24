---
name: sdl-mcp-remote-control
description: >
  Reference for driving an OpenGEODE SDL model remotely through the
  opengeode-sdl MCP server: the ten tools, their arguments, the symbol
  kinds and scenes, the safe editing procedure (check before saving),
  and the error formats to expect.
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

The server is started by orbit in the project directory, holding the
model's `.pr` files open. It parses them and renders OpenGEODE's own
graphical scene, so what the tools see is exactly what the editor
shows. **Modifications are in memory until you call `save_model`**;
the editor picks the change up from disk through its file monitor, and
the code generators read the same files.

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
`list_symbols` / `find_symbol` / `add_symbol`. Ids are stable for the
server's lifetime; a gone symbol's id is reported as such.

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
`state`/`procedure` opens a nested scene.
```
{"kind": "task", "parent_id": "<start id>", "text": "counter := counter + 1"}
{"kind": "state", "scene": "process og", "x": 900, "y": 900, "text": "Ready"}
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
{}
```

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
  `start`, `procedure_start`, `state_start` — floating

## 4. Operating procedure

1. **Read before writing.** `list_symbols` (or `find_symbol`) on the
   scene you are about to change. Ids come from these calls only.
2. **Validate text first.** For a new statement, `check_syntax` with
   the element name; fix errors before it enters the model.
3. **Edit**: `add_symbol` / `set_symbol_text` / `move_symbol` /
   `remove_symbol`. One structural change at a time.
4. **Check**: `check_model`. Fix reported errors (`set_symbol_text`,
   `remove_symbol`) and check again.
5. **Save**: `save_model`. Only then are the `.pr` files updated.
6. **Re-read** after saving if further work needs fresh ids
   (`save_model` re-renders; ids of surviving symbols stay valid).

Error lines carry their origin: `syntax [scene] <symbol>: …` for a
symbol's syntax, `semantic …` for the model parse. A tool call that
fails returns `isError` with the reason as text — read it, fix the
cause, do not retry blindly.

## 5. Worked example

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

Then to attach an input to a new state and add it to the flow:

```
1. add_symbol  {"kind": "state", "scene": "process og",
                "x": 900, "y": 900, "text": "Ready"}
2. add_symbol  {"kind": "input", "parent_id": "<state id>",
                "text": "go"}
3. add_symbol  {"kind": "task", "parent_id": "<input id>",
                "text": "counter := counter + 1"}
4. check_model → fix anything reported → save_model
```

## 6. Limits and conventions

- The server holds **one model**, the files it was started with.
  Tool arguments never carry file paths: there is nothing to point at
  another file.
- Ids are opaque; do not invent them or assume a pattern.
- `check_model`'s `warnings` are advisory (e.g. "expression is always
  true"); errors must be fixed before saving.
- The ASN.1 data view and the system structure are outside the
  server's scope: it validates types against them but does not edit
  them.
- If a tool reports the model as stale or a symbol as gone, re-read
  with `list_symbols` and continue from the fresh ids.
