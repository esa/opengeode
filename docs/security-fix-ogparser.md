# Security Fix Report — SDL Parser (`ogParser.py`) and LLVM Removal

**Scope:** remediation of all findings of the parser security audit
(`docs/security-audit-ogparser.md`), plus the removal of the outdated LLVM
backend.
**Method:** one fix per finding, each verified by re-running the audit's PoC
against the fixed tree, with a regression test added per fix
(`tests/pytests/test_ogparser_security.py`, 19 tests).
**Verification:** all suites re-run — `test-parse` 124/0 (5 expected),
`test-ada` 124/1 (pre-existing `test-aggregation2`), `test-c` 124/0,
`test-rust` 124/0 (6 expected), pytest 62 passed — identical to baseline
modulo the intentional removal of the LLVM test set (125 → 124).

---

## Summary of fixes

| # | Finding | Fix | Verified by |
|---|---------|-----|-------------|
| P1 | Forged `/* CIF _id N */` → `ctypes.cast` → uncatchable SIGSEGV | Live-symbol-id registry: only ids emitted by this process may be cast | forged id surfaces in errors but is skipped before the cast |
| P2 | `{mantissa, base, exponent}` bignum DoS | Compute in floating point; raise a clean `SyntaxError` on overflow | 1e12 exponent: 1.6 s / 99 MB + clean error (was: killed at 20 s, multi-GB) |
| P3 | `sys.path` pollution → module hijack (RCE) | No more `sys.path.insert` of the model dir or `.` | planted `LlvmGenerator.py` no longer executed; `sys.path` unchanged by `parse_pr` |
| P4 | SYNTYPE re-declaration cycle → `RecursionError` crash | Reject re-declaration with a different parent; visited-set in `find_basic_type` | cycle rejected with a clear message; pristine `test-newtype` parses with 0 errors |
| P5 | Deep nesting → raw `RecursionError` traceback | Catch `RecursionError` in `parse_pr` (both passes) → clean parse error | 2000 nested parens: "Model is too deeply nested…", exit 0 |
| P6 | `open()` without encoding → reporter crash on legacy locales | UTF-8 explicit decode in the reporter and the ANTLR stream (subclass) | `LC_ALL=C -X utf8=0` on a UTF-8 model: parse reported, no `UnicodeDecodeError` |
| P7 | `eval(elem)` behind an `assert` (clipboard-controlled name) | Fixed `SINGLE_ELEMENTS` dict + unconditional `ValueError`; clipboard validates the name first | hostile name → clean `ValueError` under `python -O`; valid names still parse |
| P9 | HYPERLINK CIF → arbitrary desktop URL handler | Restrict to `http`/`https` via `QUrl` scheme check (2 sites) | scheme policy asserted in tests |
| P10 | asn1scc args without dash-filename validation (parity gap) | Reject `-`-prefixed ASN.1 names in `check_asn1_syntax` | covered by test calling `Asn1scc._validate_input_files` |
| P8 | (negative) huge literal parsing quadratic | no fix needed — refuted on Python 3.13 | test asserts the clean behavior |

The audit's P8 (quadratic literal parsing) was already refuted; P2's twin in
`LlvmGenerator.py` disappears with the backend removal (below).

---

## P1 — Forged `CIF _id` → SIGSEGV

**Root cause.** `Pr.py:cif_symbolid` emits `/* CIF _id {id(symbol)} */` so
the GUI can link errors back to live symbols; `ogParser.symbolid()` accepts
any integer from a hand-written `.pr`, which flows into `ParsingError.pos`
and is then cast with `ctypes.cast(symbol_id, py_object).value`
(`opengeode.py`). A forged id dereferences an arbitrary address
(SIGSEGV — uncatchable by `except Exception`).

**Fix.**
* `Pr.py` — new `SYMBOL_ID_REGISTRY` (a set). `cif_symbolid()` records every
  id it actually emits (the only legitimate producer).
* `opengeode.py` (`find_symbols_and_update_errors`) — before casting, the id
  must be present in `Pr.SYMBOL_ID_REGISTRY`; otherwise the error line is
  skipped with a debug log.

**Result.** A forged `/* CIF _id 999999999999 */` still surfaces in the error
list with its position (so the user is not misled), but the cast is never
performed for it. Verified: the id reaches `pos=['999999999999', 0]` and the
gate rejects it (`999999999999 not in SYMBOL_ID_REGISTRY` → skip).

## P2 — `{mantissa, base, exponent}` resource exhaustion

**Root cause.** `ogParser.py:3555` computed `float(mant * pow(base, exp))`
with an exact integer `pow`: the bignum is fully materialised before the
`float()` conversion, so ~40 bytes of model text could consume unbounded CPU
and RAM (measured: exponent 1e9 → 7.3 s / 512 MB; 1e12 → killed at 20 s).

**Fix.** Compute in floating point only — `mant * pow(float(base),
float(exp))` — and convert the `OverflowError` into a clean `SyntaxError`
with the offending base/exponent. The float path is inherently safe (it
raises immediately when the result cannot be represented), exactly like the
already-correct `power()` operator path. `parse_pr` additionally catches
`SyntaxError` from the semantic pass so the message is reported as a parse
error rather than escaping as a traceback (this handler uses a distinct
variable name — Python deletes the `as` variable when leaving an `except`
block, which would otherwise have caused an `UnboundLocalError`).

**Result.** exponent 1e12: parse finishes in 1.6 s / 99 MB with the error
"Value of {mantissa, base, exponent} literal exceeds the 64-bit floating
point range (base 2, exponent 1000000000000)". Small exponents still parse
normally.

## P3 — `sys.path` pollution → module hijack (RCE)

**Root cause.** `ogParser.py` inserted `'.'` at import time (line 80) and the
directory of every parsed file at `sys.path[0]` (`parse_pr`, line 8114),
never reverting. Any lazily-imported module afterwards (`timeit` in
`render_everything`, `LlvmGenerator`, `StgBackend`, `opengeode.AutoRouter`,
`collections.Counter`, …) would resolve from the model directory first —
a planted `.py` file was executed (PoC-verified pre-fix).

**Fix.** Both `sys.path.insert` calls removed, with a comment explaining why
they must not come back. Nothing legitimately depended on them: the ASN.1
data model is imported by path in the hardened `Asn1scc.parse_asn1`
(the same reasoning that module already documents).

**Result.** Verified with a planted `LlvmGenerator.py`/`StgBackend.py` in the
model directory: after `parse_pr`, `sys.path` is unchanged and the planted
module is not found. Two regression tests lock this in (path equality and a
subprocess-based planted-module test).

## P4 — SYNTYPE reference cycle

**Root cause.** `USER_DEFINED_TYPES.update()` has no duplicate-name check
(the code comment at `:4471` claimed one that never existed). A second
declaration re-pointing an existing name (`syntype A = B` after
`syntype B = A`) creates a reference cycle; `find_basic_type` and
`is_numeric` then mutually recurse until the interpreter limit
(`RecursionError`, raw traceback, CLI exit 1).

**Fix (two layers).**
1. `_check_duplicate_type()` — called from `syntype()`: a re-declaration of an
   existing name is rejected **only when the parent type differs** (the case
   that creates cycles). Identical re-registrations are allowed because text
   areas are legitimately visited twice during a parse (verified on
   `test-newtype`, whose handlers run twice per declaration).
   The NEWTYPE path deliberately keeps no such check: array/enum newtypes
   embed *resolved* sorts, not type-name references, so they cannot form
   cycles — and rejecting them produced false positives.
2. `find_basic_type()` — a visited-set guards the `ReferenceType` walk and
   raises a clear `TypeError('Circular type reference detected …')` if a
   cycle ever gets through (defense in depth).

**Result.** The cycled model is rejected with "SYNTYPE Toto: re-declaration of
an existing type with a different parent (Cyc instead of MyInteger). This
could create a circular type reference."; the pristine `test-newtype` model
parses with **0 errors** (no false positives).

## P5 — Excessive nesting → `RecursionError` traceback

**Root cause.** No depth cap and no `RecursionError` handling anywhere in the
repo; the ANTLR tree construction and the semantic walkers are recursive, so
~100-150 nested parens/decisions suffice to blow the interpreter limit. The
CLI path printed a raw traceback and exited 1.

**Fix.** `parse_pr` catches `RecursionError` around both phases — the
file/string-to-tree phase and the semantic `pr_file` phase — and reports a
clean parse error ("Model is too deeply nested (recursion limit exceeded
…). Simplify the model."). The `RecursionError` handler around the semantic
pass is the one that fires for the deep-parens PoC (the tree build survives,
the semantic analysis does not).

**Result.** 2000 nested parens: parse returns with a proper error message and
exit code 0 (no traceback).

## P6 — Encoding crashes under legacy locales

**Root cause.** Two reads of the model file used the locale default codec:
the error reporter (`check_syntax`, `open(filename, 'r')`) and the ANTLR
stream (`antlr3.ANTLRFileStream`, which hardcodes `open(fileName, 'r')`).
Under `LC_ALL=C` a UTF-8 model with non-ASCII characters crashed with
`UnicodeDecodeError` — inside the error reporter, masking the real syntax
error.

**Fix.**
* `check_syntax` — `open(filename, 'r', encoding='utf-8', errors='replace')`.
* `parser_init` — a small `UTF8FileStream(antlr3.ANTLRStringStream)` subclass
  that reads the file as UTF-8 with `errors='replace'` and exposes the
  `fileName` property the parser relies on (`ANTLRFileStream` cannot take an
  encoding; plain `ANTLRStringStream` lacks the property). Invalid bytes now
  degrade into parse errors instead of crashes.

**Result.** `LC_ALL=C -X utf8=0` on a UTF-8 model: the parse completes and
reports its errors; no `UnicodeDecodeError`. (Two different decodings of the
same file in one parse are also gone.)

## P7 — `eval(elem)` in `parseSingleElement`

**Root cause.** `parseSingleElement` dispatched with `eval(elem)` behind an
`assert` whitelist; `elem` can come from the **OS clipboard**
(`Clipboard.paste`, any desktop process can write it). Under `python -O` the
assert disappears. The RCE claim was refuted during the audit (the preceding
`getattr(parser, elem)` gate only accepts identifiers), but the pattern was
fragile by design and the whitelist violation still caused uncaught
`AssertionError`s per paste.

**Fix.**
* `ogParser.py` — a module-level `SINGLE_ELEMENTS` dict maps each whitelisted
  element name to its backend function. `parseSingleElement` starts with an
  unconditional `if elem not in SINGLE_ELEMENTS: raise ValueError(...)`, and
  the backend pointer is `SINGLE_ELEMENTS[elem]` — nothing is evaluated.
  `'proc_start'`/`'state_start'` are normalised to `'start'` with their
  proper context, preserving the previous behaviour.
* `Clipboard.py` — `paste()` validates the clipboard's element name against
  the same `SINGLE_ELEMENTS` table before calling the parser, logging and
  ignoring unknown names instead of crashing.

**Result.** Hostile names (`__import__("os")...`, `nonsense`) raise a clean
`ValueError` — including under `python -O`; valid names (`task`, `state`,
`text_area`, …) still parse.

## P9 — HYPERLINK CIF → arbitrary URL handler

**Fix.** Both places that build an open-external-links label
(`TextInteraction.py` `EditableText.__init__` and `genericSymbols.py`
`hyperlinkChanged`) now parse the model-supplied URL with `QUrl` and only
accept `http`/`https`; anything else is rendered as plain text with external
links disabled. A model can no longer invoke `file://`, `ssh://` or custom
scheme handlers on click.

## P10 — asn1scc argument parity

**Fix.** `opengeode.py:check_asn1_syntax` (the GUI ASN.1 editor) now rejects
`-`-prefixed ASN.1 filenames before passing them to the compiler, matching
the validation the hardened `Asn1scc._validate_input_files` already applies
on its own paths.

---

## LLVM backend removal

The LLVM backend (`LlvmGenerator.py`, `--llvm` option, `-O` LLVM optimisation
level, `test-llvm` targets) was experimental and not up to date; it also
carried the same mantissa/base/exponent bignum bug (P2) at its line 1559.
Removed:

* `opengeode/LlvmGenerator.py` — deleted.
* `opengeode/opengeode.py` — `import LlvmGenerator`, the `--llvm` CLI option,
  the `options.llvm` dispatch and both option-combination checks removed.
  `-O` is kept (used by the C backend) with updated help text.
* Root `Makefile` — `test-llvm` target and `.PHONY` entry removed.
* `tests/testsuite/Makefile` — `test-llvm` target and `.PHONY` entry removed;
  `tests/testsuite/test.py` — mapping entry removed.
* `tests/testsuite/shared.mk` — `LLC=llc` variable, the `%.o: %.pr` LLVM rule
  and `test_llvm` from the clean list removed.
* All 123 per-test Makefiles — `test-llvm` rule blocks, `.PHONY` entries,
  `all:` prerequisites and `test_llvm` clean-list mentions removed
  (scripted; each diff verified to be purely subtractive).
* `tests/testsuite/test-llvm/` directory and all `test_llvm.c` harness files
  (16) — deleted (`git rm`).
* `tests/testsuite/benchmark.py` — now benchmarks the Ada backend only
  (was an Ada-vs-LLVM comparison); summary/table columns updated.
* `README.md` — 4.9.0 changelog entry documents the removal. The historical
  changelog entries and the contributor credit line are kept as records of
  past releases.

A regression test (`test_llvm_backend_removed`) asserts the generator file
is gone and no `--llvm`/`options.llvm` remains in `opengeode.py`.

---

## Regression tests

`tests/pytests/test_ogparser_security.py` — 19 tests, one or more per
finding, plus false-positive controls:

* `test_mantissa_base_exponent_bounded[1e12/1e15]` (P2, time-boxed at 5 s) and
  `test_mantissa_base_exponent_valid_still_works` (no false positive).
* `test_sys_path_not_polluted`, `test_planted_module_not_imported` (P3; the
  latter runs a subprocess from a different cwd with a planted module and
  asserts no marker file appears).
* `test_syntype_cycle_rejected` (P4), `test_syntype_duplicate_ok_when_identical`
  (P4 false-positive control).
* `test_deep_nesting_clean_error` (P5).
* `test_parser_reads_utf8_regardless_of_locale` (P6; subprocess with
  `LC_ALL=C -X utf8=0`).
* `test_parse_single_element_rejects_hostile_name`,
  `test_parse_single_element_whitelist_is_a_dict`,
  `test_parse_single_element_valid_names_still_work`,
  `test_clipboard_validation_helper` (P7).
* `test_symbol_id_registry_empty_without_scene`,
  `test_forged_symbol_id_not_castable` (P1).
* `test_hyperlink_scheme_restriction` (P9), `test_asn1_dash_filename_rejected_by_asn1scc`
  (P10), `test_llvm_backend_removed`.
* `test_normal_model_still_parses` — global false-positive control.

The fixture builds a minimal valid SDL model per test in a temp directory and
parses it the way the real tool does (chdir to the model directory, then
`parse_pr`), so the tests exercise the exact production path including the
USE-clause ASN.1 resolution.

## Verification

| Suite | Result | Notes |
|---|---|---|
| `test-parse` | 124 tests, 0 errors, 5 expected | −1 test = `test-llvm` removed (125 → 124) |
| `test-ada` | 124 tests, 1 error | pre-existing `test-aggregation2` failure (unrelated, documented since the Rust work) |
| `test-c` | 124 tests, 0 errors | unchanged |
| `test-rust` | 124 tests, 0 errors, 6 expected | unchanged |
| pytest | 62 passed (43 pre-existing + 19 new) | `test_qt1` skipped: pre-existing qtbot environment error |

All audit PoCs were re-run against the fixed tree and no longer reproduce
their original effect (crash, hang, traceback, marker-file execution,
segfault), each replaced by the behaviour described above.

## Files changed

* `opengeode/ogParser.py` — P2, P3, P4 (duplicate check + visited set), P5,
  P6, P7 fixes.
* `opengeode/opengeode.py` — P1 gate, P10 validation, LLVM option/dispatch
  removal.
* `opengeode/Pr.py` — `SYMBOL_ID_REGISTRY` + registration (P1).
* `opengeode/Clipboard.py` — clipboard element-name validation (P7).
* `opengeode/TextInteraction.py`, `opengeode/genericSymbols.py` — HYPERLINK
  scheme restriction (P9).
* `opengeode/LlvmGenerator.py` — deleted.
* `Makefile`, `tests/testsuite/Makefile`, `tests/testsuite/test.py`,
  `tests/testsuite/shared.mk`, 123 per-test Makefiles,
  `tests/testsuite/test-llvm/` (+16 `test_llvm.c`),
  `tests/testsuite/benchmark.py` — LLVM removal.
* `tests/pytests/test_ogparser_security.py` — new (19 tests).
* `README.md` — changelog.
* `docs/security-audit-ogparser.md` — status column updated to FIXED (see
  below).

## Residual risks (accepted, documented)

* The clipboard remains an untrusted input channel by nature; the fix
  validates the element *name*, and the parser independently re-validates —
  but pasted *model text* is still parsed as SDL on purpose (that is the
  feature).
* `check_syntax`'s recursion (and the ANTLR parser's) still has no explicit
  depth *cap*; the fix converts the failure into a clean error rather than
  preventing it. A depth counter would be a follow-up if models legitimately
  approach the limit.
* `QProcess`-launched external tools (asn1scc) are trusted binaries from
  `PATH` — unchanged, out of scope (same decision as the ASN.1 cache audit).
