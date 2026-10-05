# Ada / C / Rust Backend Comparison and Remaining Work — OpenGEODE

> Renamed from `ada-vs-rust-backend-comparison.md`: with C included and the
> OpenGEODE ↔ asn1scc BIT STRING work finished, this is now a three-backend
> status document, not just Ada vs Rust.
>
> Status date: 2026-10-05 · branch `feature_bitstring_align_ada_with_c`.

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
| Timer **value read** | ❌ | ✅ | ❌ |
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
| `CREATE` | ✅ | ❌ | ✅ |
| `STOP` terminator | ✅ `Delete_Instance` | ❌ no-op | ✅ `delete_instance` |
| `state` reference expression | ✅ | ❌ raises | ✅ |
| `parent` / `sender` / `entity` PID reads | ✅ `Self` synonym | ⚠️ parser-injected | ❌ (only `self`) |
| `MantissaBaseExp` | ⚠️ stub | ❌ raises | ⚠️ stub |
| All 41 expression handlers registered | ✅ | ✅ | ✅ |
| All statement handlers registered | ✅ | ⚠️ no `Create` | ✅ |
| Choice / enum / bitwise / append / slice codegen | ✅ | ✅ | ✅ |

Legend: ✅ implemented · ⚠️ partial/limited · ❌ missing.

---

## Confirmed Gaps — C Backend

These are verified by generating minimal models, not only by reading.

1. **`CREATE` unsupported.** `CGenerator.py` has no
   `@generate.register(ogAST.Create)`, so the default dispatch raises
   `TypeError` (`CGenerator.py:108-113`). Ada (`AdaGenerator.py:1850`) and Rust
   (`RustGenerator.py:2631`) implement it.
2. **`STOP` is a no-op.** The stop terminator is a `pass  # TODO`
   (`CGenerator.py:1387-1389`) and emits a bare `return;`. Ada emits
   `Delete_Instance (Self)`, Rust `delete_instance(self)`.
3. **`state` reference unsupported.** `_primary_state_reference`
   (`CGenerator.py:1890-1897`) raises `TypeError('To Be Implemented')`. Ada
   returns `LPREFIX.state`, Rust `ctxt.state`.
4. **`MantissaBaseExp` unsupported.** Raises at `CGenerator.py:2803`. Ada/Rust
   emit an empty stub.

---

## Confirmed Gaps — Ada Backend

1. **Timer value read missing.** Ada has no `find_var_in_timers` equivalent
   (only C does, `CGenerator.py:1509`, `:4330`), so reading a timer's current
   value is not supported.

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

### Runtime residuals (3 of 45 tests)

These do **not** reflect a generator defect; each was verified:

| Test | Cause | Classification |
|------|-------|----------------|
| `test-debug` | Model uses a non-deterministic `ANY` decision (the **C backend refuses to generate it**); its `expected` file is the Ada path. | Harness/expected fidelity |
| `test-simu` | Its `test-ada` rule is entirely commented out; `expected` is stale. | Stale fixture |
| `test-uart` | Trailing line derives from the Ada runtime's continuous-signal loop; the C reference also lacks it (pre-existing Ada-vs-C/Rust runtime divergence). | Runtime-loop divergence |

### Feature-level

1. **No `parent` / `sender` / `entity` PID reads.** Rust implements only `self`
   and offspring *writes*; it has no read expressions for the other PID roles.
2. **Timer value read missing** (same as Ada).
3. **`MantissaBaseExp` stub** (same as Ada).
4. **Process type generic parameter wiring** — Ada emits a full generic spec
   (`self`, `Delete_Instance`, `Check_Queue`, every RI, context params as formal
   generic parameters) plus a full instance instantiation. Rust's process
   type/instance separation imports the type module and calls its functions
   directly; all instances of a type share the same RI stubs. See
   `is_generic`/`ri_generic_sig` in `RustGenerator.py`.
5. **TASTE context-parameter wiring** — Rust detects `has_context_params` but
   does not generate the parameter plumbing Ada does.
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

- **126 test directories** total. **45** have a shared `expected` (a runtime
  result).
- Coverage by backend, over those 45 runtime tests:
  - **Ada: 45, C: 45, Rust: 45** build and run.
  - **Rust pass: 42/45** (the 3 residuals above).
- `test-branchcoverage`, `test-branchcoverage2`, `test-nestedpriority` are
  `--check` parse-error tests (their `expected` is compiler diagnostics); they
  intentionally get no runtime harness.
- The other ~78 directories only compile-check.
- **Zero tests currently exercise `CREATE`, `STOP`, or `state` references** in
  any backend — the three C gaps above are therefore untested even where other
  backends support them.

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

### A. Finish the backend-alignment plan (not started)

1. **C `CREATE`** — add the missing handler.
2. **C `STOP`** — implement `Delete_Instance`-equivalent instead of `return;`.
3. **C `state` reference** — implement instead of raising.
4. **C `MantissaBaseExp`** — implement or document as unsupported for all.
5. **Timer value read** — decide implement-in-Ada/Rust vs document as C-only.
6. **Targeted tests for `CREATE` / `STOP` / `state`** — currently none.

*(The Ada `Asn1InT` spelling is not on this list — it is a deliberate marker;
see the note under “Confirmed Gaps — Ada Backend”.)*

### B. Rust test-suite residual

- Decide the 3 known-failing tests: add to `RUST_EXPECTED_FAILURES` (and/or
  refresh `test-simu`'s stale `expected` since its `test-ada` is commented out).
- Optionally make `test-debug` deterministic (drop/skip its `ANY`) so it has a
  meaningful Rust expectation.

### C. Rust feature-level gaps

- `parent` / `sender` / `entity` PID read expressions.
- TASTE context-parameter wiring (or document as Ada-only).
- `mod`/`rem` negative-operand semantics (B is the correctness item).
- Decision answer-statement ordering.

### D. Coverage / fixtures

- Only 45/126 dirs have runtime expectations; ~78 are compile-only.
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
- **CHOICE**: correct process-qualified selection-enum naming and match-based
  `to_selector`/`to_enum` (replacing an invalid enum→enum `as` cast); enum
  printing; choice-alternative writes rebuild the tagged enum; renames aliases
  resolved to their target expression.
- **Misc**: `for`-each over a block expression parenthesised; timer-name
  canonicalisation; multi-line informal text commented per line; self-contained
  xorshift PRNG (removes the undeclared `rand` crate).

---

## Summary Table — All Open Items

| # | Item | Backend | Kind | Severity |
|---|------|---------|------|----------|
| A1 | `CREATE` unsupported | C | Missing feature | High |
| A2 | `STOP` is a no-op | C | Missing feature | High |
| A3 | `state` reference raises | C | Missing feature | High |
| A4 | `MantissaBaseExp` raises/stub | C / Ada / Rust | Missing feature | Low |
| A5 | Timer value read missing | Ada / Rust | Missing feature | Medium |
| A6 | No tests for `CREATE`/`STOP`/`state` | all | Test gap | Medium |
| B | 3 Rust runtime residuals | Rust | Fixture/runtime | Low |
| C1 | `parent`/`sender`/`entity` PID reads | Rust | Missing feature | Medium |
| C2 | TASTE context-param wiring | Rust | Missing feature | Medium |
| C3 | `mod`/`rem` negative operands | Rust | Semantic bug | Medium |
| C4 | Decision answer-stmt ordering | Rust | Semantic diff | Medium |
| C5 | Process-type generic wiring | Rust | Missing feature | High |
| D | ~78 dirs compile-only | all | Test gap | Low |
| E | Keep/delete scratch prototypes | — | Housekeeping | Low |
