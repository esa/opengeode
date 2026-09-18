# Post-fix verification report — ASN.1 cache security fix (V1–V11)

**Purpose**: full regression + performance verification of the fixed tree
(`opengeode/Asn1scc.py`), compared item by item against the pre-fix reference
state in **`docs/security-fix-baseline.md`** (that file is the baseline of
record and was not modified).

**Executed**: 2026-09-18, by the verification task (plan task #5).
WORKDIR: `/home/taste/workspace/opengeode`.

---

## 0. Environment — making sure the FIXED code was actually exercised

The baseline (§1.1) documented the trap: an **orphaned physical copy** of the
opengeode package lives at `~/.local/lib/python3.13/site-packages/opengeode/`
and would shadow the repo from every cwd except the repo root. That copy still
contains the **OLD, vulnerable `Asn1scc.py`** (md5 `71eb517cf1a3654b05ea1a32ef0a6cd8`
— byte-identical to the pre-fix baseline), while the repo copy is the fixed one
(md5 `b6f508a64acd7523b5215e572ca3ab5a`).

**Remedy used** (no repo file touched): every command in this report ran with

```
PYTHONPATH=/home/taste/workspace/opengeode:$PYTHONPATH
PATH=~/.local/bin:$PATH
```

(`source /tmp/verify_env.sh`), which puts the repo ahead of site-packages.
Verified: `import opengeode.Asn1scc` from `/tmp` and from
`tests/testsuite/test1` resolves to
`/home/taste/workspace/opengeode/opengeode/Asn1scc.py`. Corroborated in the
pytest log, where the `distutils.spawn` DeprecationWarnings point at the **repo**
`Asn1scc.py:396/692/708/717`, not at site-packages. asn1scc 4.9.0.0,
GNATMAKE 14.2.0, cargo 1.85.0, python 3.13.5, flake8 3.8.4 (via the shim), pytest 9.0.0
with pytest-qt still not installed — identical to baseline §1.

**Methodology note.** The first attempt ran the four make suites **concurrently**;
that produced a spurious `test-decision` failure in test-rust (the suites operate
on the *same* test directories and `test-ada`'s `clean` rule deleted
`toto_datamodel.asn` mid-rust-run) and inflated all perf timings ≈3× under load.
The baseline ran the suites **sequentially**, so all numbers in this report come
from a clean **sequential** re-run; the concurrency artefact is documented here
and is *not* a regression of the fixed tree (proof: `make -C test-decision
test-rust` passes in isolation, and the sequential suite run shows 0 errors).

Git tree state during verification: exactly one modified tracked file
(`opengeode/Asn1scc.py`, the fix) and the expected new untracked files
(`docs/security-*.md`, `tests/pytests/test_asn1scc_cache.py`,
`tests/pytests/conftest.py`); all other ~1119 untracked entries are the
pre-existing testsuite codegen leftovers listed in baseline §1.2.

---

## Post-fix verification

Everything below was measured on the fixed tree and is compared, item by
item, against the corresponding section of
`docs/security-fix-baseline.md`.

### 1. Make regression suites (sequential, repo copy exercised)

Expected-failure lists (`tests/testsuite/Makefile:10-11`):
`EXPECTED_FAILURES = test-branchcoverage/ test-branchcoverage2/ test-procedure/ test-procedure-inparam/ test-typecheck/ test-nestedpriority/`,
`RUST_EXPECTED_FAILURES = test-instance/`.

| Suite | Command | Summary line (post-fix) | Baseline | Verdict |
|---|---|---|---|---|
| test-parse | `make test-parse` | **125 tests, 0 errors** · 5 expected failure(s) · exit 0 | 125/0, 5 expected, exit 0 | **IDENTICAL** |
| test-ada | `make test-ada` | **125 tests, 1 errors** · 0 expected failure(s) · exit 2 | 125/1, 0 expected, exit 2 | **IDENTICAL** (same single pre-existing error) |
| test-c | `cd tests/testsuite && make test-c` (no root target) | **125 tests, 0 errors** · 0 expected failure(s) · exit 0 | 125/0, 0 expected, exit 0 | **IDENTICAL** |
| test-rust | `cd tests/testsuite && make test-rust` | **125 tests, 0 errors** · 6 expected failure(s) · exit 0 | 125/0, 6 expected, exit 0 | **IDENTICAL** |

Wall-clock: test-parse 44.5 s · test-ada 92.2 s · test-c 85.9 s · test-rust 77.0 s
(baseline: ≈45 s / 93 s / 85 s / 77 s) — no measurable slowdown.

Expected-failure **sets** (exact per-suite members, all inside the
Makefile lists):

- test-parse (5): `test-branchcoverage`, `test-branchcoverage2`,
  `test-procedure-inparam`, `test-procedure`, `test-typecheck`
  — exactly the baseline set (test-nestedpriority passes test-parse, as before).
- test-ada (0 expected failures; all 6 EXPECTED_FAILURES dirs pass test-ada):
  1 unexpected error = **`test-aggregation2`** — the pre-existing Makefile bug
  documented in baseline §2.1 (`No rule to make target 'test_ada.o'` — the dir
  ships no `test_ada.c` and no rule for `test_ada.o`). Reproduced in isolation:
  `make -C tests/testsuite/test-aggregation2 test-ada` → same error. **Not
  related to the fix; identical to baseline.**
- test-c (0 expected, 0 unexpected).
- test-rust (6): `test-branchcoverage`, `test-branchcoverage2`,
  `test-instance`, `test-procedure-inparam`, `test-procedure`, `test-typecheck`
  — exactly the baseline set.

**No new failures. No previously-failing test became passing (no change in the
expected-failure SET either way). Raw logs:** `/tmp/verify_test-{parse,ada,c,rust}.log`.

---

### 2. pytest (tests/pytests), including the NEW test file

Command: `cd tests/pytests && PATH=~/.local/bin:$PATH PYTEST_QT_API=PySide6
python3 -m pytest -v`

**Result: 37 passed, 1 error, 44 warnings — exit 1 (167.41 s).**

| File | Result |
|---|---|
| test_aggreg.py (6) | all passed (baseline: passed) |
| **test_asn1scc.py (2)** — `asn2dataModel` on `data/dv1.asn`, `data/dv2.asn` | **both passed** (baseline: 2/2) |
| **test_asn1scc_cache.py (19) — NEW** | **all 19 passed** |
| test_codegen1.py (1) | passed (baseline: passed) |
| test_expression.py (1) | passed (baseline: passed) |
| test_provided.py (3) | all passed (baseline: passed) |
| test_qt1.py (1) | **ERROR at setup: `fixture 'qtbot' not found`** — pre-existing environment gap, pytest-qt not installed (baseline: same single error) |
| test_system1.py (3) | all passed (baseline: passed) |
| test_various.py (2) | both passed (baseline: passed) |

Comparison vs baseline (18 passed + 1 error): **18 pre-existing tests still
pass, +19 new tests pass, the qtbot error remains the ONLY error.** Nothing
regressed; the pass-count delta is exactly the new security test file.

The 19 new tests cover: cache key option coverage (V3, ×2), sha256 key format
(V6), cache-poisoning rejection with and without manifest / world-writable /
symlink (V1), old-md5-entry ignored, manifest written & verified, html
tampering detected (V9), CWD-shadowing rejected (V2), dash-filename TypeError
(V5, both APIs), missing-file TypeError, `sys.path` restored after
`asn2dataModel` incl. failure path (V7), correct dataview per call (V7),
in-memory reuse + warm-cache-skips-compiler (perf guards), 0700 cache dir
(V8), returned-AST attribute contract.

Warnings: 44 vs baseline 9 — **same two pre-existing warning classes only**
(`distutils.spawn.find_executable` DeprecationWarning, SQLAlchemy
`declarative_base()` MovedIn20Warning); the count grows because the 19 new
tests exercise those code paths more often. **No new warning class.**
The DeprecationWarnings point at the **repo** `Asn1scc.py` — the fixed code is
what ran (also ensured by the new `tests/pytests/conftest.py`, which
front-inserts the repo root on `sys.path`).

Raw log: `/tmp/verify_pytest.log`.

---

### 3. flake8 — opengeode/Asn1scc.py

Command (flake8 3.8.4 is broken on Python 3.13; same shim as the baseline,
`/tmp/flake8_compat.py`): `cd opengeode && python3 /tmp/flake8_compat.py
Asn1scc.py`

**Post-fix: 23 issues (exit 1) vs baseline 33 — no new warnings; 10 issues
fewer.** Full list (line:col: code):

```
73:30 E261, 75:38 E261, 77:1 E302, 324:28 E211, 325:0 E272, 445:80 E501,
498:1 E302, 502:78 W291, 511:23 E203, 511:30 E211, 516:13 E265, 520:17 E127,
523:32 E203, 524:37 E203, 526:31 E203, 551:13 E265, 552:13 E265, 558:9 E265,
559:9 E265, 560:9 E265, 563:1 E302, 765:27 E127, 766:27 E127
```

All are in the untouched `ASN1`/`create_choice_determinant_types`/`asn2dataModel`
legacy regions (same code-style classes as the baseline: E261/E265/E302/E211/
E203/E127/W291/E501); the rewritten cache code contributes none. Ceiling was
≤ 33 → **PASS**. Raw: `/tmp/verify_flake8.txt`.

---

### 4. Security re-verification — independent PoC re-runs

All PoCs re-executed against the fixed tree with the **new sha256 keys**,
in scratch directories under `/tmp/ogverify` (the developer's real cache was
never touched). The victim model is `tests/testsuite/test1` copied to
`/tmp/ogverify/pocbase`; its `--check` parse key under the fixed code is
`58f6aea1aab09cdba5137974d954a572c5698d5d8a26b430c7b4d1101e6e3f0b`
(sha256; the old md5 key was `54f589e7087b89d2e602290554258498`).
Each payload writes a marker file (`/tmp/ogverify/POC_PWNED_*`) — **the marker
must stay absent**.

| # | PoC | Setup | Observed | Verdict |
|---|---|---|---|---|
| a-1 | **V1** planted `.py`+`.html` **without** manifest | poisoned `{sha256}.py`/`.html` planted in scratch `PROJECT_CACHE` | `[INFO] No ASN.1 file in cache (or no cache folder)` → regenerated; marker **absent**; entry healthy on next run | **PASS** |
| a-2 | **V1** planted `.py` **with bad manifest** (stale artifact hash) | poison payload + original (non-matching) manifest | `[INFO] Not reusing the ASN.1 cache entry: cached ASN.1 module does not match its manifest` → regenerated; marker **absent**; next run logs `Reusing cached ASN.1 modules from …` | **PASS** |
| a-3 | **V1** world-writable artifact (`chmod 666`) **with a consistent manifest** | poison payload, manifest re-hashed to match, then chmod 666 | `Not reusing the ASN.1 cache entry: "….py" is group- or world-writable` → regenerated; marker **absent**; new artifact 0644 | **PASS** |
| a-4 | **V1** symlinked artifact | `{sha256}.py` replaced by symlink to outside payload | `Not reusing the ASN.1 cache entry: "….py" is a symbolic link` → regenerated; marker **absent** | **PASS** |
| a-5 | **V1** forged `__pycache__/<key>.cpython-313.pyc` | poison `.pyc` compiled and planted next to a valid cache entry | cache **hit** on the verified `.py` bytes (`Reusing cached ASN.1 modules from …`); forged `.pyc` never executed (marker **absent**), and opengeode did not add bytecode | **PASS** |
| a-6 | **V1/legacy** old-format `{md5}.py`+`.html` (no manifest) | old pre-fix key planted with payload | ignored; new sha256 entry used instead (`Reusing cached ASN.1 modules from …/<sha256>.py`); old files left untouched and harmless on disk; marker **absent** | **PASS** |
| b | **V2** CWD shadowing, **no PROJECT_CACHE** | planted `{sha256}.py` in the model directory (cwd), `PROJECT_CACHE` unset | `[INFO] No ASN.1 file in cache (or no cache folder)` → regenerated in a temp dir and imported **by path**; planted file **not** executed (marker **absent**), not even read; parse completed 0 errors | **PASS** |
| c | **V3** options not in key | two `parse_asn1` calls, same input, `rename_policy` `NoRename` vs `SystematicRenameAllEnumerants` | keys `58f6aea1…` vs `852ef923…`; **different module objects**; 2 cache entries on disk (asn1scc invoked twice) | **PASS** |
| d | **V5** `-typePrefix`-style filename | `parse_asn1(('-typePrefix',))` and `asn2dataModel(['-typePrefix'])` with `find_executable`/`QProcess` booby-trapped | **`TypeError`** (`Invalid ASN.1 file name "-typePrefix": file names must not start with "-"…`) before any tool lookup or start, in BOTH APIs; nonexistent file → `TypeError: ASN.1 file not found: …` | **PASS** |
| e | **V7** `asn2dataModel` hygiene | `asn2dataModel(dv1.asn)` then `asn2dataModel(dv1.asn, dv2.asn)`; then a broken `.asn` to force a tool failure | `sys.path` identical (len+content) after **each** call **and** after the failure; second module contains `Ahah` (dv2 type) while the first does not — distinct module objects, `MyData` in both (the old code returned the *first* dataview); failure → `TypeError`, `sys.path` still restored | **PASS** |
| extra | **V4** `-g` debug cache poisoning | planted `{sha256}.py` in `./debug` + `--check -g` | regenerated, marker **absent**; `./debug` created `0700` | **PASS** |
| extra | **V8** cache dir perms | `umask 000` + `--check -g` (fresh `./debug`) | dir mode exactly **0700**, artifacts 0644 | **PASS** |
| extra | **V9** html tampering | cached `.html` replaced with "TAMPERED HTML" page | `Not reusing the ASN.1 cache entry: cached HTML file does not match its manifest` → regenerated; `ast.html` is the real DOCTYPE document | **PASS** |

Manifest spot-check (post-fix entry for test1): JSON with `key_options`
(`ast_version 4, rename_policy 0, flags [5], extraflags [], pretty_print true`),
`tool` fingerprint (asn1scc path/size/mtime), `inputs` `[[file, sha256]]`,
`artifacts` `{py, html}` sha256s — as documented in
`docs/security-hardening-asn1scc-cache.md`.

Cross-project cache reuse (the perf requirement) confirmed: test1's
`dataview-uniq.asn` copied to `/tmp/ogverify/pocbase` hashes to the **same**
key as the repo's `tests/testsuite/test1` — paths are not in the key.

---

### 5. Performance verification — “no performance loss”

Same models and method as baseline §6 (`opengeode <model>.pr
system_structure.pr --check`, cwd = model dir, wall clock via `subprocess`,
3 repetitions, median; machine otherwise idle).

#### 5.1 Timings (seconds, wall clock)

| Model | Mode | t1 | t2 | t3 | **Median** | Baseline median | Δ |
|---|---|---|---|---|---|---|---|
| test1 | COLD (fresh cache) | 2.337 | 2.358 | 2.349 | **2.349** | 2.350 | −0.04% |
| test1 | WARM (populated) | 0.641 | 0.631 | 0.641 | **0.641** | 0.634 | **+1.1%** |
| test1 | NO PROJECT_CACHE | 2.338 | 2.299 | 2.354 | **2.338** | (≈ cold) | — |
| test-operators | COLD (fresh cache) | 2.341 | 2.349 | 2.340 | **2.341** | 2.321 | +0.9% |
| test-operators | WARM (populated) | 0.617 | 0.611 | 0.607 | **0.611** | 0.589 | **+3.7%** |
| test-operators | NO PROJECT_CACHE | 2.375 | 2.304 | 2.344 | **2.344** | (≈ cold) | — |

(A second, independent run gave warm medians 0.628/0.592 s and cold 2.355/2.329 s
— both runs agree within ≈4% of the baseline; the deltas above are well inside
run-to-run noise. The threshold for investigation was >20%.)

#### 5.2 Warm hit still skips asn1scc

`grep -c 'Reusing cached ASN.1 modules from'` = **1 on every warm run** of both
models (e.g. `Reusing cached ASN.1 modules from
/tmp/ogverify/perf_warm_test1/58f6aea1…e3f0b.py`), 0 on cold runs. The
warm−cold gap remains ≈1.7 s ≈ the standalone asn1scc time measured in
baseline §6.2 (1.683/1.730 s) — i.e. **asn1scc is still skipped entirely on a
warm hit**; the only added work is the input sha256 (replacing the old md5)
plus one read+sha256 of the cached `.py` (and `.html` when pretty-printing).

#### 5.3 No-PROJECT_CACHE path

The `TemporaryDirectory` path (no `PROJECT_CACHE`) also shows no regression:
medians 2.338 s (test1) / 2.344 s (test-operators), i.e. cold-equivalent, same
as pre-fix (the path gains input hashing + manifest-less generation only).

---

### 6. Final verdict

- **REGRESSIONS: none.** test-parse 125/0 (+5 expected, same set) · test-ada
  125/1 (only the pre-existing `test-aggregation2` Makefile bug) · test-c
  125/0 · test-rust 125/0 (+6 expected, same set) · pytest 37 passed +1
  pre-existing qtbot error (18 baseline + 19 new all passing) · flake8 23 ≤ 33
  · every expected-failure SET unchanged · no previously-passing test now fails.
- **PERFORMANCE: no loss.** Warm median **0.641 s (test1)** vs baseline
  **0.634 s** (+1.1%) and **0.611 s (test-operators)** vs baseline
  **0.589 s** (+3.7%) — both far inside the 20% investigation threshold and
  within observed run-to-run noise; cold 2.349/2.341 s vs 2.350/2.321 s; the
  `Reusing cached ASN.1 modules from …` log still appears on every warm hit and
  the warm−cold gap still equals the standalone asn1scc time, proving the
  compiler is still skipped on warm hits.
- **SECURITY: all PoCs (a)–(e) plus V4/V8/V9 and the forged-`__pycache__` /
  old-md5-entry variants PASS** — no planted payload executed in any scenario;
  the cache degrades to regeneration, never to execution of unverified bytes.

---

*Verification by plan task #5 (`verify`). Raw artifacts:
`/tmp/verify_test-{parse,ada,c,rust}.log`, `/tmp/verify_pytest.log`,
`/tmp/verify_flake8.txt`, `/tmp/ogverify/perf_results_clean.txt`,
`/tmp/ogverify/poc*.log`. Scratch only under `/tmp/ogverify`; the developer's
real cache and the baseline file `docs/security-fix-baseline.md` were not
touched.*

---

## Final remediation triage (plan task #7, 2026-09-18)

Task #7 (remediate) triaged every finding of the independent review (plan
task #6 — "Security fix review — findings and verdict": 1 BLOCKER, 1 MAJOR,
4 MINOR, 7 INFO) together with the verification results above, applied the
fixes to `opengeode/Asn1scc.py` and `tests/pytests/test_asn1scc_cache.py`
(the final writer of both), re-verified, and reconciled the four documents.
Because the corrections change code semantics (key encoding, miss-path
behaviour), the **full four make suites and the whole pytest run were
re-executed** — results below are post-remediation, not inherited.

### 1. Per-finding decisions and what changed

| # | Review finding | Severity | Decision | What changed |
|---|---|---|---|---|
| 1 | **Cache-MISS path executes unverified bytes** — the V1 checks only guarded cache *hits*; on a miss the freshly generated `.py` was read and `exec`'d without any ownership/symlink check, so a different-uid attacker with write access to an existing shared-writable `PROJECT_CACHE` could plant a 0666 artifact and rewrite it during the ~1.7 s compile (reliable RCE) | **BLOCKER** | **FIXED** | `parse_asn1` cache-miss path (Asn1scc.py:552-611): stale entry **unlinked first** (`_remove_stale_cache_entry` — clear `TypeError` when it cannot be removed, e.g. sticky-dir foreign file); artifacts **pre-created 0600** by this process (`_precreate_cache_artifacts`; asn1scc writes *through* them — verified: same inode, mode preserved, it truncates); generated content **read back from those very open descriptors** (`_read_generated_artifact` via `os.read(fd)`) — a file replaced at the path during the generation, *even one recycling the same inode number*, cannot become the executed bytes; empty artifacts refused; descriptors closed in a `finally`. Hardening-doc §2 "degrades to regenerate, never executes the hostile file" sentence corrected (it was false for the miss path) |
| 2 | **Multi-uid shared cache degradation undocumented** — group-writable non-sticky dirs ping-pong (100 % miss), sticky dirs fail outright (asn1scc cannot truncate the foreign file) | **MAJOR** | **FIXED** (fail-clear + documented) | The pre-unlink of stale entries turns the sticky-dir case into a clear, actionable `TypeError` *before* the compiler runs (instead of an asn1scc write failure afterwards), and the ping-pong case keeps working-but-regenerating. Documented as a hard requirement — **`PROJECT_CACHE` must now be per-uid** — with the exact degradation semantics and migration advice in the hardening doc §2 (residual risk) and the audit doc V1 residual-risk block |
| 3 | **Key encoding not injective** — `str(len)+content` is not self-delimiting (12-byte file `"3456789012ab"` ≡ three files `"2"/"456"/"89012ab"`); `asn2dataModel` hashed a plain concatenation (`["ab","c"]` ≡ `["a","bc"]`) | **MINOR** | **FIXED** | Both keys now hash the **file count + per-file sha256 digests** (parse_asn1 `:478-487`, asn2dataModel `:807-812`) — self-delimiting, collision-free by construction, no extra I/O (the digests were already computed for the manifest). The reviewer's exact collision pair was reproduced on the old encoding (verified colliding) and produces different keys on the new one. Doc overstated injectivity claims corrected |
| 4 | **Stale diff-locked expected files** — `ASN.1 Parser: using cache folder None` in `test-debug/expected_c` and `test-nocif/expected_c` no longer matches a fresh run | **MINOR** | **ACCEPTED-DOCUMENTED** (review premise corrected) | The fixtures are **outside this task's file ownership** (testsuite files). Empirically re-verified during triage: the **pre-fix tree emits zero such lines too** (ran `test-c` in a scratch copy with the pre-fix site-packages Asn1scc — 0 lines) — the log line has been `PROJECT_CACHE`-conditional since *before* the security work, so the drift is **pre-existing**, not fix-caused, and is masked by the `\|\| exit 0` in both Makefiles. Documented in hardening doc §4.4 with the caveat and the fix recipe (regenerate the two fixtures, a testsuite change) |
| 5 | **`pretty_print_asn1.stg` not permission-hardened** — absent from the artifact hardening list; also written with a symlink-following `open('wb')` at a fixed name | **MINOR** | **FIXED** (+extension) | `stgfile` added to the `_harden_cache_file_perms` list when pprint; and *all* fixed-name writes in shared locations (manifest, stg, DMT concat file, DMT staleness sidecar) now go through `_write_file_checked` (`O_CREAT\|O_EXCL\|O_NOFOLLOW`, mode 0600, uid-checked) — a symlink can no longer redirect any of them |
| 6 | **`asn2dataModel` hardening asymmetries** — (a) explicit `outdir` created without `0o700`; (b) generated files in an explicit outdir get no hardening; (c) the `ASN2DM` reuse path re-imports modules with existence-only checks | **MINOR** | (a) **FIXED**; (b) **ACCEPTED-DOCUMENTED**; (c) **FIXED** | (a) `os.makedirs(outdir, exist_ok=True, mode=0o700)` (`:841`). (b) Accepted: the *mode* of files in a caller-chosen outdir is the user's umask choice; hardening them would silently change user-facing output modes — documented as residual. (c) `_import_dataview_modules` now verifies every module before exec (`_verify_cached_artifact(check_mode=False)`: not a symlink, owned by the current user — `:757-760`), `TypeError` otherwise; the sub-ms race between generation and import in a caller-trusted outdir is documented as residual (no production caller passes a shared outdir; the mkdtemp default is 0700) |
| 7 | **INFO — V2 maintenance residual**: a future `python.stg` emitting `import` statements would resolve via `sys.path` | INFO | **DOCUMENTED** | Added to hardening doc §3.4 (with the rule to apply: import hook pinned to the artifact's own folder, or reject `import` outside an allowlist). Today's generated modules import nothing — re-verified against a real artifact |
| 8 | **INFO — test-coverage gaps**: no `-g` test; key tests did not vary `flags`/`extraflags`; uid-rejection untestable unprivileged | INFO | **FIXED** (all but the uid limit) | 6 new tests: `test_cache_key_covers_flags_and_extraflags`, `test_cache_key_separates_input_file_sets`, `test_debug_cache_poisoning_rejected` (V4, `-g` + `./debug` 0700), and the three generation-window tests (below). The foreign-uid rejection is exercised via a `getuid` simulation (`test_generation_rejects_replaced_artifact`) — documented as the closest unprivileged approximation |
| 9 | **INFO — pre-existing quirks** (in-memory fast path does not refresh `asn1Files`; asserts require ASN1 enum instances) | INFO | **VERIFIED PRE-EXISTING, DOCUMENTED** | Both confirmed in the pre-fix tree (read from the orphaned site-packages copy): the asserts at parse_asn1:338-340 pre-date the fix, `ogParser` passes enum instances, external int-passing callers would hit the same assert pre-fix. No change (an `asn1Files` refresh on the in-memory fast path would add I/O to the hot path; the on-disk hit path does refresh — `:638`) |
| 10-12 | **INFO — positive verifications** (POSIX guards correct, TypeError convention holds on every reachable path, no extra hit-path I/O, test quality GOOD, doc line refs exact) | INFO | No action | These confirmed the fix; the line references in the docs were **recomputed** after the remediation edits (all refs re-verified against the final file; the few that the reviewer's count was based on shifted by the new code) |

**Bonus hardening applied while fixing #1** (falls out of the same review
pass): the `_verify_cached_artifact` hit-path check now `fstat`s the *open
descriptor* rather than `lstat`ing the path (kills the check→read TOCTOU),
and the manifest write is exclusive-creation (`O_EXCL`) so a file that
reappeared after the pre-generation unlink is refused rather than written
through.

### 2. Re-verification evidence (post-remediation, all runs sequential)

- **New security tests** (`cd tests/pytests && PATH=~/.local/bin:$PATH
  PYTEST_QT_API=PySide6 python3 -m pytest test_asn1scc_cache.py`):
  **25 passed** (19 pre-remediation + 6 new), ~58 s.
- **Whole pytest suite**: **43 passed + 1 error** (the pre-existing
  `test_qt1.py` qtbot gap) in 77 s = baseline 18 + 19 cache tests + 6 new —
  nothing regressed. Warnings 58: same two pre-existing classes only
  (`find_executable` DeprecationWarning, SQLAlchemy MovedIn20Warning), no
  new class.
- **make test-parse**: **125 tests, 0 errors, 5 expected failures, exit 0** —
  identical to baseline and to the post-fix run.
- **make test-ada**: **125 tests, 1 error (the pre-existing
  `test-aggregation2` Makefile bug), 0 expected, exit 2** — identical to
  baseline and post-fix.
- **make test-c** (`cd tests/testsuite`): **125 tests, 0 errors, 0 expected,
  exit 0** — identical.
- **make test-rust**: **125 tests, 0 errors, 6 expected failures, exit 0** —
  identical.
- **flake8** (`Asn1scc.py`, same shim): **23 issues** — unchanged from the
  post-fix count, still under the 33 baseline ceiling; all in the untouched
  legacy regions. The two E231s the first remediation edit introduced were
  fixed (f-string → str concat). Test file: pycodestyle + pyflakes clean
  (the 5 E128s from the new tests fixed).
- **Old-code detection re-proven**: the 25 tests run against the *original
  vulnerable* `Asn1scc.py` (md5 `71eb517c`, in a scratch tree) → **23 failed,
  2 passed** (only the perf guards pass by design). Against a reconstructed
  *pre-remediation* variant (the #5-verified state: hit-path checks, no
  miss-path hardening) → **3 failed** (exactly the three generation-window
  tests), 22 passed — i.e. the new tests target precisely the BLOCKER.
- **PoCs re-run on the final tree** (scratch `/tmp/remed/poc_final`, markers
  must stay absent): planted entry without manifest / with stale manifest /
  world-writable with *consistent* manifest / symlinked artifact / old md5
  entry / tampered html / `-typePrefix` in both APIs (booby-trapped
  QProcess) → **all PASS** (regenerated or `TypeError`, no payload
  executed, regenerated artifacts 0600). Remediation-specific: planted
  stale entry **never written through** (fd still holds the payload, file
  unlinked, new artifact created), mid-generation replacement by "another
  user" → `TypeError('… cannot be trusted: …')`, unremovable entry (sticky
  dir simulation) → `TypeError('… cannot be replaced …')`, `-g`/`./debug`
  poisoning rejected with dir 0700 → **all PASS**.
- **F4 probe** (fixture-drift provenance): `make test-c` of
  `tests/testsuite/test-debug` in a scratch copy, with the `|| exit 0` mask
  removed, run once with the fixed repo code and once forcing the
  *pre-fix* orphan Asn1scc — **both emit 0 `using cache folder None`
  lines**: the fixture drift predates the security work (the pre-fix tree
  already guarded the log line), exactly as documented in the triage of
  finding 4.
- **Perf spot-check** (same two models, 3 reps, medians; warm reuses the
  cache populated by the first rep):

| Model | Cold | Warm | Baseline warm | Post-fix warm |
|---|---|---|---|---|
| test1 | 2.331 s | **0.635 s** | 0.634 s | 0.641 s |
| test-operators | 2.314 s | **0.587 s** | 0.589 s | 0.611 s |

  `Reusing cached ASN.1 modules from …` appears exactly once on every warm
  run, 0 on cold; warm−cold ≈ 1.7 s ≈ standalone asn1scc → **the compiler
  is still skipped on warm hits; no performance loss** (warm deltas −0.0 %
  and −0.3 % vs baseline — within noise). The miss-path hardening adds no
  measurable cost (cold ≈ baseline too).

### 3. Final per-finding status of the audit (V1–V11)

| # | Status after remediation |
|---|---|
| V1 | **FIXED** — hit path (manifest + ownership/mode/symlink + sha256, verified-bytes exec) **and** miss path (stale entry removed, artifacts pre-created 0600, content read from those descriptors; empty artifacts refused; all fixed-name writes `O_NOFOLLOW`/`O_EXCL`) |
| V2 | **FIXED** — import strictly by path from verified bytes; `sys.path` never consulted; maintenance caveat for future `python.stg` imports documented |
| V3 | **FIXED** — all options in the key and re-compared from the manifest; key encoding now collision-free (count + per-file digests), also for `asn2dataModel` |
| V4 | **FIXED** — `./debug` goes through the same checks; created 0700; now covered by a dedicated regression test |
| V5 | **FIXED** — input validation at both API boundaries, `TypeError` before any tool start |
| V6 | **FIXED** — sha256 everywhere; self-delimiting key encoding |
| V7 | **FIXED** — `finally` sys.path restore, by-path imports with pre-exec verification, content-keyed `ASN2DM` (collision-free), sidecar staleness, `atexit` cleanup, 0700 outdir, `O_NOFOLLOW` concat/sidecar writes |
| V8 | **FIXED** — 0700 creation everywhere (incl. explicit outdir and `./debug`), write-bit stripping incl. the stg template, one-time shared-writable warning |
| V9 | **MITIGATED** — manifest-covered, strict UTF-8, `QTextBrowser` no JS (documented residual: consistent-but-crafted html requires same uid) |
| V10 | **VERIFIED-ALREADY-FIXED** — `opengeode.py:3940-3942` `finally: os.remove`; mode 0600 |
| V11 | **ACCEPTED** — PATH trust, documented; asn1scc fingerprinted in manifests |

### 4. Residual risks (final, all documented in the hardening doc §2)

1. **Same-uid attacker** (or root): out of threat model by construction —
   they can rewrite artifact+manifest consistently, and likewise rewrite
   through the live pre-created descriptor during generation; they can
   already edit the user's files.
2. **Multi-uid shared `PROJECT_CACHE`**: no longer a working cache —
   group-writable dirs ping-pong (correct but useless), sticky dirs stop
   with a clear `TypeError`; **use a per-uid cache** (migration advice in
   the docs).
3. **PATH trust** (V11) unchanged.
4. **User-chosen hostile `PROJECT_CACHE`/outdir**: degrades to regeneration
   or a clear failure, never to executing foreign bytes; DMT modules in a
   caller-chosen outdir are link/ownership-checked but not hash-bound
   (accepted: no manifest exists for them, no production caller passes a
   shared outdir).
5. **Confidentiality** not enforced beyond 0700 directory creation and
   0600 artifacts (integrity was the target).
6. **Stale testsuite fixtures** `test-debug/expected_c`,
   `test-nocif/expected_c` (pre-existing drift, masked by `|| exit 0`) —
   fix is a testsuite change, deliberately left out of this effort's file
   scope.
7. **Future `python.stg` emitting imports** would resolve via `sys.path`
   (rule to apply documented; today's modules import nothing).

### 5. Files changed by the whole effort (final state)

- `opengeode/Asn1scc.py` — the only tracked file modified (the complete
  fix: manifest + sha256 key + by-path verified-bytes import + input
  validation + miss-path hardening + DMT hygiene).
- `tests/pytests/test_asn1scc_cache.py` — NEW, 25 regression tests.
- `tests/pytests/conftest.py` — NEW, repo-root sys.path insertion (guards
  against the orphaned site-packages copy).
- `docs/security-audit-asn1scc-cache.md` — audit + per-finding remediation
  status (updated through the remediation pass).
- `docs/security-hardening-asn1scc-cache.md` — NEW, as-built architecture,
  threat model, maintenance guidance, re-verify recipe (updated through
  the remediation pass).
- `docs/security-fix-baseline.md` — pre-fix baseline (written by task #1,
  untouched since).
- `docs/security-fix-verification-report.md` — this report (task #5) plus
  this triage section (task #7).
- No other tracked file changed. `ogParser.py` needed no change (the
  `TypeError` convention is preserved end-to-end). `opengeode/icons.py` and
  the ~1100 testsuite codegen leftovers are pre-existing untracked files
  (baseline §1.2), not part of this effort.

*Remediation executed 2026-09-18 by plan task #7 (`remediate`). Raw logs:
`/tmp/remediate_test_{parse,ada,c,rust}.log`, `/tmp/remediate_pytest.log`,
`/tmp/remediate_flake8.txt`; PoC scratch under `/tmp/remed/poc_final` — the
developer's real cache was never touched.*
