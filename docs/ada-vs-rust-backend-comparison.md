# Ada vs Rust Backend Comparison — OpenGEODE

## Overview

| Aspect | Ada | Rust |
|--------|-----|------|
| File | `AdaGenerator.py` (4198 lines) | `RustGenerator.py` (3538 lines) |
| Architecture | `@singledispatch generate` + `@singledispatch expression` | Same |
| `@generate.register` handlers | 12 | 12 (identical set) |
| `@expression.register` handlers | 42 | 42 (identical set) |
| Helper functions used | `code_generation_preprocessing`, `generate_asn1_datamodel`, `add_labels_before_each_branch`, `inner_labels_to_floating` | Same four |
| Feature coverage | 100% (reference) | ~95% |

Both backends share the same structural skeleton: a `@singledispatch generate` function handling AST node types (Process, Output, ProcedureCall, TaskAssign, TaskInformalText, TaskForLoop, Create, Decision, Label, Transition, Floating_label, Procedure) and a `@singledispatch expression` function handling expression types (PrimVariable, PrimCall, PrimIndex, PrimSubstring, PrimSelector, PrimStateReference, all operators, PrimEnumeratedValue, PrimChoiceDeterminant, PrimInteger, PrimReal, PrimBoolean, PrimNull, PrimEmptyString, PrimStringLiteral, PrimConstant, PrimMantissaBaseExp, PrimConditional, PrimSequence, PrimSequenceOf, PrimChoiceItem).

Both use the same four `Helper` functions for AST preprocessing, ASN.1 datamodel generation, branch label insertion, and inner-label-to-floating conversion.

---

## Fully Implemented in Both (no gap)

### Process-level

- Process type vs instance generation (`instance=False/True`)
- Context struct (fields, initialization)
- `DEFAULT_CONTEXT` with initial values
- Startup function
- PI (Provided Interface) generation including fpar parameters
- RI (Required Interface) stub generation
- Timer handling (set_timer, reset_timer, timeout)
- Continuous signals
- State aggregations / composite states
- State entry/exit procedures
- Exported procedures
- Observer mode (partial in both; simu mode removed from Rust)
- TASTE mode (partial in Rust — see gaps)
- SDL constants (synonyms)
- Monitors
- Stop conditions
- `no_context` processes
- Auto-elaboration / startup calls (Ada: automatic; Rust: comment-only — see differences)

### Expression-level (all 42 handlers)

- PrimVariable, PrimIndex, PrimSubstring, PrimSelector, PrimStateReference
- PrimCall (all built-ins): abs, fix, float, chr, power, cos, sin, sqrt, round, ceil, floor, length, present, choice_to_int, shift_left, shift_right, exist, to_selector, to_enum, val, num, trunc, observer_status, inner procedure calls
- PrimStringLiteral, PrimInteger, PrimReal, PrimBoolean, PrimNull, PrimEmptyString
- PrimConstant, PrimMantissaBaseExp (stub in both), PrimEnumeratedValue, PrimChoiceDeterminant
- PrimConditional, PrimSequence, PrimSequenceOf, PrimChoiceItem
- ExprPlus, ExprMul, ExprMinus, ExprGt, ExprGe, ExprLt, ExprLe, ExprDiv, ExprMod, ExprRem
- ExprEq, ExprNeq, ExprAssign
- ExprOr, ExprAnd, ExprXor, ExprImplies, ExprNot, ExprNeg
- ExprAppend, ExprIn

### Statement-level

- Output/ProcedureCall (write, writeln, set_timer, reset_timer, output signals, procedures)
- TaskAssign, TaskInformalText, TaskForLoop, Create
- Decision (normal, any, informal_text, alternative)
- Label, Transition (nextstate, join, stop, return)
- Floating_label
- Procedure (header, external, inner, locals)

---

## Differences in Implementation (both work, different approach)

### Indexing

| | Ada | Rust |
|--|-----|------|
| **Offset** | 1-based — adds 1 to SDL's 0-based indices (`1 + idx`) | 0-based — matches SDL directly, no offset |

### Struct field naming

| | Ada | Rust |
|--|-----|------|
| **Array data** | `.Data` | `.arr` |
| **Array length** | `.Length` | `.n_count` |

### Optional field existence

| | Ada | Rust |
|--|-----|------|
| **Type** | Integer (`0` / `1`) | Boolean (`true` / `false`) |
| **Access** | `rec.exist.field := 1` | `rec.exist.field = true` |

### Choice types

| | Ada | Rust |
|--|-----|------|
| **Construction** | Record aggregate: `(Kind => X, field => V)` | Enum variant: `Type::Variant(V)` |
| **Selection** | `To_{Type}_Selection(param.Kind)` | `choice_present(&param)` helper |
| **Access** | `receiver.field_name` | `receiver.field_name` (same) |

### Enum variants

| | Ada | Rust |
|--|-----|------|
| **Syntax** | Flat prefixed name: `asn1SccValue` | Scoped: `EnumType::asn1SccValue` |

### Operators

| SDL operator | Ada | Rust |
|-------------|-----|------|
| `=` | `=` | `==` |
| `/=` | `/=` | `!=` |
| `and` | `and` / `and then` | `&&` |
| `or` | `or` / `or else` | `||` |
| `xor` | `xor` | `^` |
| `mod` | `mod` | `%` |
| `rem` | `rem` | `%` |
| `**` (power) | `base ** Natural(exp)` | `(base as i64).pow(exp as u32)` |

### Assignment

| | Ada | Rust |
|--|-----|------|
| **Operator** | `:=` | `=` |
| **fpar params** | Direct (Ada `in out` is transparent) | `*deref` needed (`&mut` references) |
| **Variable-size arrays** | Updates `.Length` separately | Updates `.n_count` separately |

### Decision branches

| | Ada | Rust |
|--|-----|------|
| **Chain syntax** | `if` / `elsif` / `else` / `end if` | `if` / `else if` / `else` / `}` |
| **Match arms** | `case` / `when idx =>` / `end case` | `match` / `=> { }` / `_ =>` |
| **Closing** | `last = 'end if;'` parameter | Hardcoded `}` |

### Labels in procedures

| | Ada | Rust |
|--|-----|------|
| **Mechanism** | Real Ada `goto` + `<<label>>` syntax | `loop { match __next { ... } }` dispatch loop |
| **Join terminator** | `goto {label}` | `__next = "{label}"; continue;` |

### Auto-elaboration

| | Ada | Rust |
|--|-----|------|
| **Startup** | `begin Startup;` in package body — automatic on elaboration | Comment only — harness must call `{process.name}_startup()` |

### RI stubs

| | Ada | Rust |
|--|-----|------|
| **Files** | Separate `.ads` (spec) + `.adb` (body) | Separate `_ri.rs` |
| **Body** | `is null` (do-nothing) | `{ /* RI stub */ }` (comment-only) |
| **Delegation** | `renames {process.name}_RI.{sig}` | Direct stub function |

### Export PI

| | Ada | Rust |
|--|-----|------|
| **Mechanism** | `pragma Export(C, ...)` | `#[no_mangle] pub unsafe extern "C" fn` |

### Math functions

| | Ada | Rust |
|--|-----|------|
| **cos/sin/sqrt** | Generic package instantiation (`Ada.Numerics.Generic_Elementary_Functions`) in `local_decl` | Built-in `f64` methods (`.cos()`, `.sin()`, `.sqrt()`) |

### String concatenation (`//` operator)

| | Ada | Rust |
|--|-----|------|
| **Mechanism** | Ada `&` operator (native array concatenation) | Explicit `copy_from_slice` block expression with temp variables |
| **NUL handling** | Not needed (Ada manages length separately) | Stops at NUL terminator for IA5String |

### Static context initialization

| | Ada | Rust |
|--|-----|------|
| **Default_Context** | Record aggregate: `(Init_Done => False, field => val, ..., others => <>)` | `static mut` with `{ field: val, ..., ..unsafe { std::mem::zeroed() } }` |
| **Choice/Enum types** | Handled naturally by Ada aggregate syntax | Special path: all fields must be initialized explicitly (cannot use `zeroed()` for enums in `const` context) |
| **ctxt declaration** | `{LPREFIX} : aliased Type := Default_Context;` | `static mut {LPREFIX}: Type = unsafe { DEFAULT_CONTEXT };` (or `zeroed()` fallback) |

### Choice selection conversion functions

| | Ada | Rust |
|--|-----|------|
| **Status** | Generated: `To_{sort}` conversion functions | Deliberately skipped — Rust enums + pattern matching replace this |

### Monitors

| | Ada | Rust |
|--|-----|------|
| **Location** | Fields in the context struct (can be aliased) | Separate `static mut` globals |
| **Initialization** | Via `Default_Context` aggregate | `Default::default()` |

### Process type generics

| | Ada | Rust |
|--|-----|------|
| **Generic spec** | Full: `self`, `Delete_Instance`, `Check_Queue`, all RIs, context params as formal generic parameters | No formal parameter wiring — instance wrapper imports type module and calls functions directly |
| **Instance instantiation** | `package ... is new ...(...)` with parameter mapping | `#[path = "{type}.rs"] mod {type};` + direct function calls |
| **RI binding** | Generic `with procedure` parameters — different instances can bind different RIs | All instances share the same type module's RI stubs |

### Simu mode

| | Ada | Rust |
|--|-----|------|
| **Unhandled input** | `raise Lost_Input` (exception) | `panic!("Lost_Input")` |
| **Branch coverage** | Typed `Branch_Coverage_Array` indexed by `Branches` enum | Fixed `[bool; 256]` array |
| **Simu PI exports** | `pragma Export(C, simu_{signame}, "...")` | Not supported (simu mode removed) |
| **Step functions** | Both `_simu_next` and `_simu_continue` exports | Not supported (simu mode removed) |

### For loops

| | Ada | Rust |
|--|-----|------|
| **Range (step=1)** | `for var in start..stop-1 loop` (inclusive range, decrements stop) | `for var in start..stop {` (exclusive range, no decrement) |
| **Range (step≠1)** | `while var < stop` with manual increment in `declare/begin/end` | `let mut var = start; while var < stop` with manual increment in `{}` |
| **SeqOf iteration** | `.Data` / `.Length` / `'Range` | `.arr` / `.n_count` / `.len()` |
| **Empty transition** | `null;` | `// (empty transition)` comment |

### Decision `any` kind

| | Ada | Rust |
|--|-----|------|
| **Mechanism** | `case Rand_{n}_Pkg.Random(Gen_{n}) is` with `when idx =>` arms | `match gen_{n}_init() {` with `{idx} => {` arms |

### Decision `informal_text`

| | Ada | Rust |
|--|-----|------|
| **Output** | `-- Informal decision ignored` + `null;` | `// Informal decision ignored` (comment only, no null) |

---

## Non-Implemented / Missing Features in Rust

### 1. Exported procedure RPC transitions (**FIXED**)

Ada (`AdaGenerator.py:3868-3896`) injects `{proc_name}_Transition` procedure calls into return terminators of exported procedures, enabling state changes after RPC calls. **Rust now implements the same logic** in `RustGenerator.py` `_inner_procedure` — walks all transitions (start + floating labels) recursively looking for `return` terminators, and appends a `ProcedureCall` AST node calling `{proc_name}_Transition`. The `ProcedureCall` handler detects `_Transition` calls and generates them without the `ri_` prefix (calling the PI function directly).

### 2. Simu PI function exports (**REMOVED — simu mode not supported in Rust**)

Ada generates `pragma Export(C, simu_{signame}, "{process.name.lower()}_simu_PI_{signame}")` for each simu PI function, making them callable from C. Rust does not support simu mode.

**Impact:** Simulation mode is not supported in the Rust backend.

### 3. `_simu_continue` export (**REMOVED — simu mode not supported in Rust**)

Ada exports `Execute_Transition` as `{process.name.lower()}_simu_continue` (line 1304). Rust does not support simu mode.

**Impact:** Simulation mode is not supported in the Rust backend.

### 4. `Dest_PID` support for RIs (**FIXED**)

Ada adds `Dest_PID` parameter to RI function signatures when a PID type exists (lines 1120-1128, 1193-1202). Rust now adds `dest_pid` to RI stubs, RI calls, timer stubs, timer calls, and Create handler — using `default_pid()` helper that returns `SELF_PID` for process types and `asn1SccEnv` otherwise.

The C backend now also supports `dest_pid` (matching Ada): RI declarations (output signals, external procedures, timers) gain a trailing `const asn1SccPID dest_pid` when the PID type exists; RI call sites resolve the destination from the `TO` clause (enumerants built via the EnumID lookup — `asn1SccPID_env`, `asn1SccPID_gui` — or passed through for PID variables); timer calls pass `default_pid()`; the instance wrapper forwarders also carry `dest_pid`. Unlike Ada, C has no default parameter values, so the argument is always explicit.

**Impact:** Process-to-process communication with PID routing is now supported in Rust and C.

### 5. Choice selection conversion functions (**DELIBERATELY SKIPPED**)

Ada generates `To_{sort}` conversion functions for choice selector types (lines 437-445). Rust explicitly skips these (`choice_selections = []`), relying on Rust's native enum pattern matching.

**Impact:** None — this is a design decision. Rust's enum system handles choice selection natively.

### 6. Continuous signal awareness in procedures (**MISSING**)

Ada checks `process_has_cs` in the procedure handler to determine if `_Transition` calls are needed after procedure returns (line 3864). Rust does not check this.

**Impact:** Procedures in processes with continuous signals may not properly trigger continuous signal evaluation after returning.

### 7. Ground expression assertions (**MISSING**)

Ada asserts that ground expressions (default values) have no side effects: `assert not dst and not dlocal` (line 3907). Rust does not assert this.

**Impact:** Side-effecting default values could pass silently in Rust without detection.

### 8. Integer type casting in arithmetic (**MISSING**)

Ada casts mismatched integer types in binary operations (e.g., `Integer32Type` vs `IntegerType`) to the wider type (lines 2352-2364). Rust does not — it emits the raw expression `({left} op {right})`.

**Impact:** Mixed-width integer arithmetic will fail to compile in Rust without manual casts.

### 9. Constant folding (**MISSING**)

Ada constant-folds binary operations when both operands are numeric literals via `eval()` (lines 2384-2389). Rust does not — it always emits the full expression.

**Impact:** No functional impact, but Rust generates slightly less optimal code (e.g., `2 + 3` instead of `5`).

### 10. `mod` vs `rem` semantics (**POTENTIAL BUG**)

Both SDL `mod` and `rem` are mapped to Rust's `%` operator. Rust's `%` is remainder (not modulo) — it differs for negative operands. Ada's `mod` and `rem` have distinct semantics.

**Impact:** `(-7) mod 3` should be `2` (modulo) but Rust produces `-1` (remainder). This is a semantic bug for negative operands.

### 11. Decision answer statement ordering (**SEMANTIC DIFFERENCE**)

Ada emits answer constant evaluation statements **before** the `if` condition (lines 3372-3373) — they execute regardless of which branch is taken. Rust emits them **inside** the `if` body, **after** the condition check (lines 2061-2064) — they only execute if the branch matches.

**Impact:** If answer expressions have side effects, the ordering differs between Ada and Rust. This is a behavioral difference.

### 12. `PrimEmptyString` for SEQUENCE with optional fields (**SIMPLIFIED**)

Ada generates explicit `Exist => (field => 0, ...)` initialization for SEQUENCE types with optional fields (lines 2856-2877). Rust just uses `Default::default()` for all types.

**Impact:** Functionally equivalent (Rust's `Default` trait initializes all fields), but Rust doesn't generate the explicit `Exist` struct initialization.

### 13. Element-wise bitwise ops on OctetString/BitString (**PARTIAL**)

Ada generates element-wise array comprehensions for `NOT`, `AND`, `OR`, `XOR` on `OctetString`/`BitString` types (e.g., `for I in ... => not Data(I)`). Rust only generates element-wise loops for `SequenceOf Boolean`, falling through to whole-value operations for OctetString/BitString.

**Impact:** Bitwise operations on bit strings may produce incorrect results in Rust.

### 14. Multi-line informal text handling (**MINOR**)

Ada handles multi-line informal text by prefixing each line with `-- ` (line 1742). Rust just uses `// ` without newline splitting (line 1837).

**Impact:** Multi-line informal text would produce a single long comment in Rust instead of properly formatted multi-line comments.

### 15. Process type generic parameter wiring (**MISSING**)

Ada generates a full generic specification with `self`, `Delete_Instance`, `Check_Queue`, all RIs, and context parameters as formal generic parameters (lines 627-644), plus a full `package ... is new ...(...)` instantiation (lines 1228-1273). Rust has no equivalent — the instance wrapper simply imports and calls the type module's functions without formal parameter wiring.

**Impact:** Rust's process type/instance separation is less type-safe and doesn't support multiple instances of the same type with different RI bindings. All instances of a process type share the same RI stubs.

### 16. `BRANCH_COVERAGE` array size (**POTENTIAL ISSUE**)

Ada uses a typed `Branch_Coverage_Array` indexed by the `Branches` enum (line 1225). Rust uses a fixed `static mut BRANCH_COVERAGE: [bool; 256]` (line 1414).

**Impact:** If a process has more than 256 branches, the Rust version will overflow silently.

### 17. TASTE context parameter wiring (**MISSING**)

Ada generates context parameter declarations in the generic spec (`{process.name}_ctxt : {ASN1SCC}Context_{process.name}`) and maps them in the instance instantiation (line 1256). Rust detects `has_context_params` but does not generate any context parameter wiring.

**Impact:** TASTE integration with context parameters is incomplete in Rust.

### 18. `Null` statement for empty transitions (**MINOR**)

Ada generates `null;` for empty transitions (line 3539). Rust generates `// (empty transition)` comment (line 2240).

**Impact:** Functionally equivalent (both are no-ops), but Rust's approach could cause issues in expression contexts where a value is expected.

---

## Summary Table

| # | Feature | Status in Rust | Severity |
|---|---------|---------------|----------|
| 1 | Exported procedure RPC transitions | Fixed | — |
| 2 | Simu PI function exports | Removed (simu not supported) | — |
| 3 | `_simu_continue` export | Removed (simu not supported) | — |
| 4 | `Dest_PID` support for RIs | Fixed | High |
| 5 | Choice selection conversion functions | Deliberately skipped | None |
| 6 | Continuous signal awareness in procedures | Missing | Medium |
| 7 | Ground expression assertions | Missing | Low |
| 8 | Integer type casting in arithmetic | Missing | Medium |
| 9 | Constant folding | Missing | Low |
| 10 | `mod` vs `rem` semantics | Potential bug | High |
| 11 | Decision answer statement ordering | Semantic difference | Medium |
| 12 | `PrimEmptyString` for SEQUENCE with optional fields | Simplified | Low |
| 13 | Element-wise bitwise ops on OctetString/BitString | Partial | Medium |
| 14 | Multi-line informal text handling | Minor | Low |
| 15 | Process type generic parameter wiring | Missing | High |
| 16 | `BRANCH_COVERAGE` array size | Potential issue | Low |
| 17 | TASTE context parameter wiring | Missing | Medium |
| 18 | `Null` statement for empty transitions | Minor | Low |
