# Ada / C / Rust Backend Comparison and Remaining Work — OpenGEODE

> Renamed from `ada-vs-rust-backend-comparison.md`: with C included and the
> OpenGEODE ↔ asn1scc BIT STRING work finished, this is now a three-backend
> status document, not just Ada vs Rust.
>
> Status date: 2026-10-06 · branch `feature_bitstring_align_ada_with_c`.

## Overview

| Aspect | Ada | C | Rust |
|--------|-----|---|------|
| File | `AdaGenerator.py` (4309 lines) | `CGenerator.py` (4589 lines) | `RustGenerator.py` (5245 lines) |
| Architecture | `@singledispatch generate` + `@singledispatch expression` | Same | Same |
| `@generate.register` handlers | 12 | 11 | 12 |
| `@expression.register` handlers | 41 | 41 | 41 |
| Shared `Helper` functions | `code_generation_preprocessing`, `generate_asn1_datamodel`, `add_labels_before_each_branch`, `inner_labels_to_floating` | Same four | Same four |
| Feature coverage (main codegen) | Reference | ~99% | ~99% (compile-clean; see runtime residuals) |
| Feature coverage (simulation mode) | Reference | Partial | Not supported |

All three backends share the same structural skeleton: a `@singledispatch
generate` function handling AST node types and a `@singledispatch expression`
function handling expression types (PrimVariable, PrimCall, PrimIndex,
PrimSubstring, PrimSelector, PrimStateReference, all operators,
PrimEnumeratedValue, PrimChoiceDeterminant, PrimInteger, PrimReal, PrimBoolean,
PrimNull, PrimEmptyString, PrimStringLiteral, PrimConstant, PrimMantissaBaseExp,
PrimConditional, PrimSequence, PrimSequenceOf, PrimChoiceItem).

Type **definitions** (Sequence/Choice/SequenceOf/enumerated/strings) are not
emitted per backend: all three call `Helper.generate_asn1_datamodel(process)`
(`AdaGenerator.py:410`, `CGenerator.py:331`, `RustGenerator.py:1090`) which
writes `<proc>_datamodel.asn`, and `asn1scc -Ada` / `-c` / `-Rust` produces the
types. Per-backend differences are only in `type_name` mapping, default/zero
values, and expression/lvalue codegen.

**Scope of this document:** main code generation only. Simulation mode is out of
scope (Rust does not implement it; C partially).

---

## Coverage Matrix

| Feature | Ada | C | Rust |
|---------|:---:|:-:|:----:|
| Process type vs instance (`instance=False/True`) | ✅ | ✅ | ✅ |
| Context struct + `DEFAULT_CONTEXT` | ✅ | ✅ | ✅ |
| Startup / auto-elaboration | ✅ automatic | ✅ `CInit` | ✅ harness calls `<proc>_startup()` |
| PI generation (incl. fpar params) | ✅ | ✅ | ✅ |
| RI stub generation | ✅ | ✅ | ✅ |
| Timer set / reset / timeout | ✅ | ✅ | ✅ |
| Timer-name case resolution | ✅ (case-insensitive language) | ✅ `find_var_in_timers` | ✅ `canonical_timer_name` |
| Continuous signals | ✅ | ✅ | ✅ |
| State aggregations / composite states | ✅ | ✅ | ✅ |
| State entry / exit procedures | ✅ | ✅ | ✅ |
| Exported procedures | ✅ | ✅ | ✅ |
| Exported-procedure RPC `_Transition` | ✅ | ✅ | ✅ |
| Observer mode | ✅ | ✅ | ⚠️ partial |
| SDL constants (synonyms) | ✅ | ✅ | ✅ |
| Monitors | ✅ | ✅ | ✅ |
| Stop conditions | ✅ | ✅ | ✅ |
| `no_context` processes | ✅ | ✅ | ✅ |
| `CREATE` | ✅ | ✅ | ✅ |
| `STOP` terminator | ✅ `Delete_Instance` | ✅ `<proc>_delete_instance` | ✅ `delete_instance` |
| `state` reference expression | ✅ | ✅ | ✅ |
| `<proc>_state()` (state as string, for tracer) | ✅ `New_String` | ✅ `switch` on state | ❌ returns NULL |
| `parent` / `sender` / `entity` PID reads | ✅ `Self` synonym | ⚠️ parser-injected | ❌ (only `self`) |
| `MantissaBaseExp` | ⚠️ stub | ❌ raises | ⚠️ stub |
| All 41 expression handlers registered | ✅ | ✅ | ✅ |
| All statement handlers registered | ✅ | ✅ | ✅ |
| Choice / enum / bitwise / append / slice codegen | ✅ | ✅ | ✅ |
| `DECISION ANY` (random branch) | ✅ `Discrete_Random` | ✅ `rand()` | ✅ xorshift PRNG |

Legend: ✅ implemented · ⚠️ partial/limited · ❌ missing.

**`DECISION ANY` randomness.** All three backends now seed their RNG from the
system clock so that a run really picks a branch at random (previously C used an
unseeded `rand()` — glibc behaves as `srand(1)` — and Rust filled its xorshift
state with a fixed constant, so both were effectively deterministic). C seeds
`srand()` once in `CInit` from `clock_gettime(CLOCK_REALTIME)` nanoseconds
(falling back to `time(NULL)`), mixing the value first because glibc's `rand()`
returns correlated first outputs for nearby seeds; Rust seeds from
`SystemTime` nanoseconds. Ada already reset `Discrete_Random` per startup. The
nanosecond clock matters: `time(NULL)` alone has one-second granularity, so
back-to-back runs would otherwise repeat. Because the branch is random by
design, the C and Rust test targets normalise it
(`sed -E 's/Random value \w+/Random value X/'`) before diffing.

---

## Confirmed Gaps — C Backend

These are verified by generating minimal models, not only by reading.

1. **`MantissaBaseExp` unsupported.** Raises at `CGenerator.py:2803`. Ada/Rust
   emit an empty stub.

> **`CREATE` — FIXED.** `_create_request` (`CGenerator.py`, registered for
> `ogAST.Create`) now emits
> `ctxt.offspring = <instance>_create_instance(self);`, mirroring Ada
> (`ctxt.Offspring := Create_X (Self);`) and Rust. The environment-provided
> link name is declared in the generated file
> (`generating_instance_glue_declarations`).

> **`STOP` — FIXED.** The stop terminator now emits
> `<proc>_delete_instance(self);` (standalone) or
> `<type>_RI_Delete_Instance(self);` (process TYPE, bound by the instance
> wrapper to `<instance>_delete_instance`), then resets the context to its
> default value (re-applying the DCL initial values) and clears `init_done`.
> To make `init_done` actually stop the process, the PI entry points now carry
> the same guard as Ada/Rust
> (`if (!ctxt.init_done) return;`) — this mirrors Ada's `Execute_Transition`
> and Rust's `execute_transition`.
>
> For a process TYPE with a PID type, `self` is no longer omitted: it is
> emitted as a mutable static (per instance, since the type `.c` is `#include`d
> into each instance wrapper) that the wrapper sets to the instance PID at
> startup — the C counterpart of Ada's `self` generic formal and Rust's
> `SELF_PID`.
>
> Covered by the new `tests/testsuite/test-create-delete` (runtime test in C).

> **`state` reference — FIXED.** `_primary_state_reference`
> (`CGenerator.py`) now returns `ctxt.state` instead of raising
> `TypeError('To Be Implemented')`, and `_enumerated_value` renders a state
> name comparand (`Wait` in `state = Wait`) via `generate_state_name()`.
> Verified end-to-end: a `decision (state = S1)` model generates, compiles and
> runs identically in Ada/C/Rust. Fixing the test also uncovered the same
> latent bug in the **Rust** backend (state comparand emitted
> `asn1SccComplexsdl_States::s1` instead of `::Complexsdl_States_s1`),
> corrected in `RustGenerator._enumerated_value` by reusing its existing
> `generate_state_name()` helper. Covered by the new
> `tests/testsuite/test-stateref`.

> **`<proc>_state()` — FIXED in Ada and C.** The state-as-string accessor used by
> the MSC tracer (TASTE's `printf("INNER_SDL_STATE: <proc>,%s\n", <proc>_state())`)
> did not behave the same in the two backends:
> * **C** returned the literal `"Not_supported_in_C__Use_the_Ada_backend"`.
>   `generating_current_state_to_str` (`CGenerator.py`) now emits a `switch` on
>   the state and returns a stable string literal per state — exactly Ada's
>   `<States>'Image` (enumeration literal, upper-cased, e.g.
>   `ASN1SCCWAIT_0_ENTERING_WAIT`). String literals avoid making the caller
>   `free()` the result. A prototype is now emitted in the generated header;
>   process *types* emit none (they have no global context — the context is a
>   parameter), and the instance wrapper gains its own `<instance>_state`,
>   mirroring Ada.
> * **Ada** returned a **NULL pointer**: commit `00777363` ("Remove simu/dll
>   related code") replaced the working `New_String (...)` body of the generated
>   `<proc>_RI.To_C_Pointer` stub with `Null_Ptr`, so `printf("%s", ...)` folded
>   to `puts(NULL)` and segfaulted (GNAT reports `STORAGE_ERROR`). The stub body
>   is restored to `New_String (State_As_String)`. `To_C_Pointer` is kept, not
>   removed: it is the **platform hook** TASTE overwrites (its kazoo skeleton
>   uses `New_String` on native Linux and `Null_Ptr` on embedded targets) and is
>   only emitted for standalone OpenGEODE (`not taste`).
>
> Covered by the new `tests/testsuite/test-state-to-string` (Ada + C assert the
> string, Rust only builds since its `_state()` still returns NULL).

---

## Confirmed Gaps — Ada Backend

**None.** The two notes below are recorded *not* as gaps, but to pre-empt
re-discovery of earlier misclassifications.

> **Not a gap — "timer value read" does not exist.** A timer name is accepted
> only as the `TIMER`-typed argument of `set_timer(value, name)` and
> `reset_timer(name)`. Using a timer in any expression is rejected by the parser
> in all three backends (`TimerType` is not a value type): `x := myTimer`,
> `decision myTimer`, `num(myTimer)`, `writeln(myTimer)`, `exist(myTimer)` all
> fail type-checking, and the grammar's `active(timer)` rule is commented out
> (`sdl92.g:1286`, inside the `/* */` at 1258–1293). C's `find_var_in_timers`
> (`CGenerator.py:1509`, `:4337`) and Rust's `canonical_timer_name`
> (`RustGenerator.py:389`) do the *same* thing — resolve the declared spelling
> of a timer name so the emitted `SET_<timer>` / `RESET_<timer>` matches the
> case-sensitive target language. Ada needs no such helper because Ada is
> case-insensitive. So there is no "timer value read" capability for C to have
> and Ada/Rust to lack. (An earlier revision of this document wrongly listed it
> as an Ada/Rust gap, from grepping `find_var_in_timers` alone.)

> **Not a defect — deliberate trace marker.** `type_name` returns `'Asn1InT'`
> for `ChoiceEnumeratedType` (`AdaGenerator.py:4157`). Ada is case-insensitive,
> so this resolves to `adaasn1rtl.Asn1Int`, and the distinctive spelling is
> **intentionally kept** as a marker pointing back to this generator site. It
> was verified that the returned name is only ever interpolated into emitted
> code — never compared, used as a key, or case-mapped — so the spelling has no
> semantic effect. Do **not** "fix" it. (`StgBackend.py:1762`, the legacy
> backend, uses `Asn1Int`.)

---

## Confirmed Gaps — Rust Backend

### Compile-level: none remaining

As of this branch, **all 45 Rust runtime tests compile with zero errors** (they
previously produced ~15 non-compiling `.rs` files). See "Recent Rust fixes"
below for the list.

### Runtime residuals (1 of 45 tests)

These do **not** reflect a generator defect; each was verified:

| Test | Cause | Classification |
|------|-------|----------------|
| `test-simu` | Its `test-ada` rule is entirely commented out; `expected` is stale. | Stale fixture |

(`test-debug` used to be a second residual; it now passes in Ada, C **and** Rust.
The C backend does support `DECISION ANY`; the Rust harness printed no banner and
its `expected` was stale. Both fixed, and the randomly chosen `ANY` branch is
normalised before diffing in the C and Rust test targets.)

(`test-uart` used to be a third residual and was mis-classified here as a
"runtime-loop divergence". The real cause was a Rust **generator** bug: the
conditional-expression codegen hoisted *both* branches' statements before the
`if`, so the untaken branch ran too — in this model an append
(`'Received: ' // msg`) overflowed a fixed 10-byte array and panicked. Fixed by
emitting each branch's statements lazily inside its own arm; the residual
"Checking queue" line was simply never reached because of the panic.)

### Feature-level

1. **No `parent` / `sender` / `entity` PID reads.** Rust implements only `self`
   and offspring *writes*; it has no read expressions for the other PID roles.
2. **`MantissaBaseExp` stub** (same as Ada).
3. **Process type generic parameter wiring** — Ada emits a full generic spec
   (`self`, `Delete_Instance`, `Check_Queue`, every RI, context params as formal
   generic parameters) plus a full instance instantiation. Rust's process
   type/instance separation imports the type module and calls its functions
   directly; all instances of a type share the same RI stubs. See
   `is_generic`/`ri_generic_sig` in `RustGenerator.py`.
4. **TASTE context-parameter wiring** — Rust detects `has_context_params` but
   does not generate the parameter plumbing Ada does.
5. **`<proc>_state()` returns NULL.** `RustGenerator.py:1616-1624` emits
   `std::ptr::null()` ("Return state as C string - simplified"). Ada and C both
   return the real state string now; a Rust caller that dereferences it would
   crash. Not exercised by any driver today.
6. **Simulation mode not supported** (by design).

---

## Remaining Backend Divergences (checked, still open)

These are behavior differences that survive the recent fixes. Severity is
relative to real-model exposure.

1. **`mod` vs `rem` on negative operands (semantic bug).** Both SDL `mod` and
   `rem` map to Rust `%` (`RustGenerator.py:4239`), which is remainder, not
   modulo. `(-7) mod 3` yields `-1` in Rust instead of Ada's `2`. Ada keeps the
   two distinct (`AdaGenerator.py:2413-2415`). **Medium/High.**
2. **Decision answer-statement ordering.** Ada emits answer constant-evaluation
   statements **before** the `if` condition (they run regardless of branch);
   Rust emits them **inside** the branch body (`RustGenerator.py:3061`, after
   the condition). Differs only when answer expressions have side effects.
   **Medium.**
3. **`BRANCH_COVERAGE` array size.** Rust uses a fixed
   `static mut BRANCH_COVERAGE: [bool; 256]` (`RustGenerator.py:2134`); Ada
   uses a typed array indexed by the `Branches` enum. A process with > 256
   branches would overflow silently. **Low.**
4. **Empty transition representation.** Ada emits `null;`; Rust emits a
   `// (empty transition)` comment. Both are no-ops. **Low.**

> Items from the previous revision that are now **resolved**, because the whole
> Rust backend was rewritten while making the runtime tests pass: element-wise
> bitwise ops on OCTET/BIT STRING (item 13), multi-line informal text (item 14),
> `PrimEmptyString` for SEQUENCE with optional fields (item 12), and the
> `Null`/empty-transition concerns. See below.

---

## BIT STRING C-Alignment (finished on this branch)

Separate from the general backend comparison, the BIT STRING layout/slice work
that motivated this branch is complete; full detail in
[`ada-bitstring-c-aligned.md`](ada-bitstring-c-aligned.md).

**The model.** ASN.1 bit *k* lives in byte `k/8` at bit position
`7 − (k mod 8)` from the MSB (mask `0x80 >> (k%8)`) — this is how asn1scc stores
a BIT STRING in C and Rust. OpenGeode's Ada backend was switched to the **same
byte array** representation by default, so the three languages agree on raw
memory (`X.Data` is a byte array in Ada too).

- **asn1scc** (branch `feature_bitstring_align_ada_with_c`): opt-in
  `-adaBitStringAlignment` emits Ada `Data : adaasn1rtl.OctetBuffer (1 .. N)`
  matching C's `byte arr[]`; default output byte-identical to master. Commits
  `b86fac63`, `0805d969`.
- **OpenGeode**: Ada comma C and Rust BIT STRING codegen updated to the byte
  model; a **slice `b(i,j)` bug** was found and fixed in **all three**
  backends (previously OOB in C, `Constraint_Error` in Ada, non-compiling in
  Rust). `test-bitstring` now exercises literal, named-bit set, single-bit
  write and slice; commits `38116473`, `62438efa`, `04a01168`, plus this
  session's fixes.

**Known residual:** OpenGeode's `CGenerator` is now self-consistent with
asn1scc storage, but `test-bitstring` does **not** cross-check its output
against a live asn1scc encode, so a future divergence in wire/layout parity
between the two generators would not be caught there.

---

## Test Coverage Status

- **128 test directories** run by the harness. **50** have a shared
  `expected` (a runtime comparison); the rest only compile-check.
- Suites (current, branch `feature_bitstring_align_ada_with_c`):
  - **C: 128 tests, 0 errors.**
  - **Ada: 128 tests, 0 errors** (one pre-existing expected failure,
    `test-nestedpriority`).
  - **Rust: 128 tests, 1 error** — exactly the 1 known residual above
    (`test-simu`).
- `test-branchcoverage`, `test-branchcoverage2`, `test-nestedpriority` are
  `--check` parse-error tests (their `expected` is compiler diagnostics); they
  intentionally get no runtime harness.
- `state` references are now covered by `test-stateref` (Ada/C/Rust).
- `CREATE` and `STOP` are now covered by `test-create-delete` (runtime test in
  C, using local environment glue; Ada/Rust are generation-checked).
  **The earlier C gaps (`CREATE` unsupported, `STOP` a no-op) are fixed.**

### Rust runtime harness pattern (for adding coverage)

Each runtime test gets a `main.rs` (committed) plus a `test-rust` rule that
generates, builds, runs and diffs:

```make
test-rust:
	$(OPENGEODE) <models> --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s|$$|\nuse crate::dataview_uniq::*;\nuse crate::dataview_uniqDef::*;|' "$$f"; \
	  fi; \
	done && \
	python3 patch_ri.py <proc>.rs && \      # when an RI body is needed
	cp <proc>_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -
```

`shared.mk`'s `clean` deletes generated `*.rs` but preserves the committed
`main.rs`. RI stub bodies (e.g. `pow`, `send_to_uart`, `check_queue`) are filled
by a per-directory `patch_ri.py`, mirroring the C driver.

---

## Remaining Work — Complete Status

### A. Finish the backend-alignment plan

1. **C `CREATE`** — done (see the section on Confirmed Gaps — C Backend).
2. **C `STOP`** — done (ditto).
3. **C `MantissaBaseExp`** — implement or document as unsupported for all.
4. **Targeted tests for `CREATE` / `STOP`** — done: `test-create-delete`.

*(C `state` reference is done; see the fixed items below.)*

*(“Timer value read” was removed from this list — it is not a feature of any
backend; see the note under “Confirmed Gaps — Ada Backend”.)*

*(The Ada `Asn1InT` spelling is not on this list — it is a deliberate marker;
see the note under “Confirmed Gaps — Ada Backend”.)*

### B. Rust test-suite residual

- Decide the 1 known-failing test: add `test-simu` to `RUST_EXPECTED_FAILURES`
  (and/or refresh its stale `expected`, since its `test-ada` is commented out).
- `test-debug` now has a meaningful Rust expectation: both the C and Rust test
  targets normalise the non-deterministic `DECISION ANY` branch (`Random value X`)
  before diffing, and both backends now seed their RNG from the clock.

### C. Rust feature-level gaps

- `parent` / `sender` / `entity` PID read expressions.
- TASTE context-parameter wiring (or document as Ada-only).
- `mod`/`rem` negative-operand semantics (B is the correctness item).
- Decision answer-statement ordering.

### D. Coverage / fixtures

- Only 45/128 dirs build+run in Rust (the ones with a `test-rust` cargo rule);
  the rest are compile-only.
- `test-bitstring` should optionally cross-check against asn1scc's C encode.

### E. BIT STRING residuals

- Decide keep/delete of the scratch prototypes under
  `opus2/validation/bitstring-alignment/` (`keepapi/`, `calign/`, `exp/`).

---

## Recent Rust Fixes (this branch) — 11 → 45 runtime tests, 45/45 building

The Rust backend had ~15 latent codegen bugs that no test caught because only 11
tests ran in Rust. After adding harnesses, all compile errors were fixed; the
notable ones:

- **Dataview module name** derived from the ASN.1 file stem (was hardcoded
  `dataview-uniq`), fixing every test whose dataview is `datamodel.asn` /
  `dv.asn` / `dataview.asn`.
- **Nested continuous signals**: missing `}` before `else if` left the function
  brace unclosed.
- **Exported procedures** now use the `<proc>_PI_<name>` prefix (avoids clashing
  with the runtime `<proc>_check_queue`); the internal queue call uses
  `<proc>_check_queue`.
- **Strings**: literal escaping, fixed-vs-variable size (`n_count`) handling,
  `length()` on slices, `.arr.len()` for fixed SEQUENCE OF, byte-list literal
  wrapping in append/conditional.
- **Types/expressions**: declared-subtype integer casts, process SDL synonym
  constants, `NULL → ()`, field spelling `b-C → b_C`, bitwise on integer
  literals, enum-vs-int comparison, `power()` for reals, signed-integer
  `Image` spacing.
- **Conditional expression branches are lazy.** `_conditional` emitted both
  branches' statements *before* the `if`, so the untaken branch was evaluated
  anyway; a branch operand invalid for the running state (e.g. an append
  overflowing a fixed-size target) then panicked. Each branch's statements now
  go inside its own `if`/`else` arm, matching Ada's lazy `if/then/else`. This is
  what fixed `test-uart`.
- **CHOICE**: correct process-qualified selection-enum naming and match-based
  `to_selector`/`to_enum` (replacing an invalid enum→enum `as` cast); enum
  printing; choice-alternative writes rebuild the tagged enum; renames aliases
  resolved to their target expression.
- **Misc**: `for`-each over a block expression parenthesised; timer-name
  canonicalisation; multi-line informal text commented per line; self-contained
  xorshift PRNG (removes the undeclared `rand` crate), now seeded from
  `SystemTime` nanoseconds so `DECISION ANY` is genuinely random.
  (Implementation note: the seed uses
  `duration_since(..).unwrap_or_default().as_nanos()` — **not** the
  `.map(|d| ..).unwrap_or(..)` closure form, which made the linker report
  duplicate `#[no_mangle]` symbols because the generated file is built both as
  the lib target and as a module of the test binary.)

---

## Summary Table — All Open Items

| # | Item | Backend | Kind | Severity |
|---|------|---------|------|----------|
| A1 | `MantissaBaseExp` raises/stub | C / Ada / Rust | Missing feature | Low |
| B | 1 Rust runtime residual | Rust | Fixture | Low |
| C1 | `parent`/`sender`/`entity` PID reads | Rust | Missing feature | Medium |
| C2 | TASTE context-param wiring | Rust | Missing feature | Medium |
| C3 | `mod`/`rem` negative operands | Rust | Semantic bug | Medium |
| C4 | Decision answer-stmt ordering | Rust | Semantic diff | Medium |
| C5 | Process-type generic wiring | Rust | Missing feature | High |
| C6 | `<proc>_state()` returns NULL | Rust | Missing feature | Low |
| D | ~83 dirs compile-only | all | Test gap | Low |
| E | Keep/delete scratch prototypes | — | Housekeeping | Low |
