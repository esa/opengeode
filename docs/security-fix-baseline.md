# Pre-fix baseline — ASN.1 cache security fix (V1–V11)

**Purpose**: reference state captured *before* the security fixes to `opengeode/Asn1scc.py` land, so the post-fix verification (plan task #5) can diff against it. Everything below was measured on the unmodified tree at commit `10a6d195`.

**Captured**: 2026-09-18, by the baseline task (plan task #1). WORKDIR: `/home/taste/workspace/opengeode`.

---

## 1. Environment and tool versions

| Tool | Version / path | Notes |
|---|---|---|
| git HEAD | `10a6d195` "Add support for Dest PID in the C backend" | log: `10a6d195`, `f755319c` (Rust TO PID), `fb47567c` (Improve Rust backend) |
| asn1scc | **4.9.0.0** (`/home/taste/tool-inst/share/asn1scc/asn1scc`) | on PATH via entry `/home/taste/tool-inst/share/asn1scc/` (already in PATH; `find_executable` picks it up — no `~/.local/bin` needed for it) |
| gnatmake | **GNATMAKE 14.2.0** (`/usr/bin/gnatmake`) | |
| cargo | **1.85.0** (`d73d2caf9 2024-12-31`, `/usr/bin/cargo`) | |
| python3 | **3.13.5** (`/usr/bin/python3`) | |
| flake8 | **3.8.4** (mccabe 0.6.1, pycodestyle 2.6.0, pyflakes 2.2.0) | **broken on this host** — see §5 |
| pytest | **9.0.0** (pluggy 1.0.0); plugins: anyio 4.8.0, typeguard 4.4.2 | **pytest-qt NOT installed** |
| opengeode CLI | `~/.local/bin/opengeode` (v4.8.3 editable-install script) | see §1.1 — resolves to *installed copy*, not repo |
| OS | Linux 6.8.0-110-generic | |

`PATH` additions needed for the suites: `~/.local/bin` (opengeode CLI, flake8). `asn1scc` is found via the PATH entry `/home/taste/tool-inst/share/asn1scc/` (already on this host's PATH). `PYTHONPATH` on this host already contains `/home/taste/tool-inst/...` entries **including two empty (`::`) entries → the current working directory is on sys.path**.

### 1.1 CRITICAL: two copies of opengeode — which one the tests exercise

`opengeode` is pip-installed **editable** (`direct_url.json`: `{"dir_info": {"editable": true}, "url": "file:///home/taste/workspace/opengeode"}`), **but a physical copy of the package also exists at `~/.local/lib/python3.13/site-packages/opengeode/`**. Because `sys.meta_path`'s `PathFinder` (which scans `site-packages`) runs **before** the editable `_EditableFinder`, from every cwd that is *not* the repo root Python imports the **site-packages copy**, not the repo:

- Verified: `cd /tmp && python3 -c "import opengeode.Asn1scc"` → `~/.local/lib/python3.13/site-packages/opengeode/Asn1scc.py`
- `make test-*` suites run `opengeode` with cwd = test dir → **installed copy**
- `cd tests/pytests && pytest` → **installed copy** (DeprecationWarnings in the pytest log point at site-packages paths)
- From the repo root, the repo copy wins (cwd first in sys.path via the empty PYTHONPATH entries)

**Divergence between the copies** (diff -rq, ignoring `__pycache__`):

- `Asn1scc.py`: **byte-identical** (md5 `71eb517cf1a3654b05ea1a32ef0a6cd8` in both) → the baseline below is valid for cache-path behaviour regardless of which copy runs.
- `CGenerator.py`, `RustGenerator.py`: **installed copies are OLDER** (installed 08:16, repo 15:31 on 2026-09-18; repo has the Dest-PID support from HEAD commits). Installed copy lacks repo-only files `ada_body.st`, `ada_source.st`.

**⚠ Post-fix verification (task #5) MUST make the repo copy win, otherwise the fixed repo code will NOT be exercised by the make suites/pytest.** The physical `site-packages/opengeode/` directory is **orphaned**: no dist-info RECORD owns it (leftover from an earlier non-editable install that was later replaced by the editable one), so `pip uninstall opengeode` will NOT remove it. Safe remedies: (a) `make install` (non-editable `pip install --upgrade .` — overwrites the stale files with fresh repo code), or (b) `rm -rf ~/.local/lib/python3.13/site-packages/opengeode` (leaves only the editable finder → repo wins everywhere), or (c) export `PYTHONPATH=/home/taste/workspace/opengeode` ahead of site-packages for the test runs.

### 1.2 Git tree state (pre-existing dirt)

`git status --porcelain` at capture time: **1120 untracked entries, zero modified/deleted tracked files**. All untracked paths existed before this task started (verified: no new entries after the baseline runs; the only artifact created by the baseline itself, `.pytest_cache/` at repo root, was removed).

Top-level untracked paths (pre-existing):

```
?? build/
?? docs/security-audit-asn1scc-cache.md     (the audit report from the previous plan)
?? help/html_output/
?? help/wiki/
?? opengeode.egg-info/
?? opengeode/icons.py
```

Plus ~1114 untracked codegen byproducts under `tests/testsuite/*` (Rust artifacts: `Cargo.toml`, `Cargo.lock`, `asn1rust/`, `target/`, `*.rs`, `*_cargo.toml`, `*_datamodel.rs`, `*_datamodelDef.rs`, and a few C/Ada leftovers like `test-bitstring/test_ada`, `test-aggregation2/og.o`). These are testsuite build leftovers, not tracked content. **Later waves: any diff you see in these directories is pre-existing; conversely `make clean` inside testsuite removes most of them — do not confuse that with the fix.**

---

## 2. Make regression suites

Commands run from repo root unless noted. Expected-failure lists from `tests/testsuite/Makefile` lines 10–11:

```
EXPECTED_FAILURES        = test-branchcoverage/ test-branchcoverage2/ test-procedure/ test-procedure-inparam/ test-typecheck/ test-nestedpriority/
RUST_EXPECTED_FAILURES  = test-instance/
```

| Suite | Command | Summary line | Expected failures | Unexpected failures | Exit |
|---|---|---|---|---|---|
| test-parse | `make test-parse` | **125 tests, 0 errors** / 5 expected failure(s) | test-branchcoverage, test-branchcoverage2, test-procedure, test-procedure-inparam, test-typecheck | **none** | 0 |
| test-ada | `make test-ada` | **125 tests, 1 errors** / 0 expected failure(s) | none reported (all 6 EXPECTED_FAILURES dirs passed test-ada!) | **test-aggregation2** (see below) | 2 |
| test-c | *(root Makefile has NO `test-c` target)* run as `cd tests/testsuite && make test-c` | **125 tests, 0 errors** / 0 expected failure(s) | none | **none** | 0 |
| test-rust | `make test-rust` | **125 tests, 0 errors** / 6 expected failure(s) | test-branchcoverage, test-branchcoverage2, test-instance, test-procedure-inparam, test-procedure, test-typecheck | **none** | 0 |

Wall-clock: test-parse ≈45s · test-ada ≈93s · test-c ≈85s · test-rust ≈77s (8 parallel workers).

### 2.1 The single unexpected failure: test-aggregation2 (test-ada)

`test-aggregation2` fails test-ada with a **pre-existing Makefile bug, unrelated to the ASN.1 cache**:

```
make[2]: *** No rule to make target 'test_ada.o', needed by 'test-ada'.  Stop.
```

- `tests/testsuite/test-aggregation2/Makefile:28` declares `test-ada: dataview-uniq.o | test_ada.o` (order-only prerequisite) and line 33 `$(GNATLINK) -o test_ada test_ada.o og.ali -lm`, but **the directory has no `test_ada.c` and no rule to build `test_ada.o`**.
- Compare sibling `test-aggregation1/Makefile`: same pattern, but that directory *ships* a tracked `test_ada.c` (implicit make rule `%.o: %.c` from `shared.mk:68` builds it).
- `git ls-files tests/testsuite/test-aggregation2/` → only `Makefile, dataview-uniq.asn, expected.log, og.pr, simu.sh, test_c.c` — no `test_ada.c`.

**Baseline verdict**: `test-aggregation2` test-ada failure is PRE-EXISTING and out of scope of the fix. Post-fix runs will see the same 1 error — it must not be attributed to the fix. (Fixing it = adding a `test_ada.c` to that dir — a testsuite content change, not part of `opengeode/Asn1scc.py`.)

### 2.2 Note on expected failures per suite

The 6 EXPECTED_FAILURES entries fail only in the suites that exercise them. In test-ada they all **passed** (reported `[OK]`) — the testsuite's expected-failure lists are per-phase (`test.py` matches the rule), so the counts above are per-suite fact, not an anomaly. test-parse expected-failed on 5 of the 6 (test-nestedpriority passes test-parse); test-rust expected-failed on 5 of 6 + test-instance.

---

## 3. pytest (tests/pytests)

Command: `cd tests/pytests && PATH=~/.local/bin:$PATH PYTEST_QT_API=PySide6 python3 -m pytest`

**Result: 18 passed, 1 error, 9 warnings — exit 1 (19.57s)**

| Test file | Result |
|---|---|
| test_aggreg.py (6 tests) | all passed |
| **test_asn1scc.py (2 tests)** — exercises `asn2dataModel` (uses `data/dv1.asn`, `data/dv2.asn`) | **both passed** (test_1, test_2) |
| test_codegen1.py (1 test) | passed |
| test_expression.py (1 test) | passed |
| test_provided.py (3 tests) | all passed |
| test_qt1.py (1 test) | **ERROR at setup: `fixture 'qtbot' not found`** — pre-existing environment issue: **pytest-qt is not installed** on this host (`pytestqt` import fails; pip list shows no pytest-qt). NOT a code problem. |
| test_system1.py (3 tests) | all passed |
| test_various.py (2 tests) | both passed |

Warnings (9, pre-existing): `distutils.spawn.find_executable` DeprecationWarnings from `Asn1scc.py:157,316,332,341` (installed copy paths), SQLAlchemy `declarative_base()` MovedIn20Warning from generated `db_model.py` (tmp dirs), plus the qtbot error itself.

**Note**: as per §1.1, pytest here exercised the **installed (site-packages) copy** of opengeode — byte-identical for `Asn1scc.py`, so valid baseline. The new tests added by task #3 will live alongside these files.

---

## 4. V10 verdict (NamedTemporaryFile leak in GUI syntax check)

**V10 is ALREADY FIXED in tree — and in the installed copy.**

- `opengeode/opengeode.py:3902`: `with tempfile.NamedTemporaryFile(mode='w+', suffix='.asn', delete=False, encoding='utf-8') as tmp_file:` creates `tmp_file_path`.
- `opengeode/opengeode.py:3940-3942`: the `finally:` block of the surrounding `try:` does `if os.path.exists(tmp_file_path): os.remove(tmp_file_path)` — guaranteed removal on every path (including the early returns at 3911/3925/3928, which are inside the `try`).
- `grep -n NamedTemporaryFile opengeode/*.py` → **only this one site** (`opengeode.py:3902`). No other unfixed sites exist.
- The installed site-packages copy has the identical fixed code (verified lines 3900-3905 / 3938-3943).

**The audit report's claim that V10 is unfixed is WRONG and must be corrected by the docs task (#4).**

---

## 5. flake8 baseline — opengeode/Asn1scc.py

**flake8 3.8.4 on this host is BROKEN**: `flake8 --version` crashes (`AttributeError: 'EntryPoints' object has no attribute 'get'` in `flake8/plugins/manager.py:254`) because flake8 3.8.4 predates the `importlib.metadata.entry_points()` API change in Python 3.13. Both `flake8` and `python3 -m flake8` fail identically. Workaround used (NOT a repo change): a `/tmp/flake8_compat.py` shim that wraps `entry_points()` to restore `.get()` (flake8 3.8.4 / mccabe 0.6.1 / pycodestyle 2.6.0 / pyflakes 2.2.0 — the exact plugin set flake8 would have used).

`cd opengeode && flake8 Asn1scc.py` → **33 issues (all warnings/errors: 31 E-codes, 2 W-codes), exit 1**. Full list (line:col: code — count: 33):

```
17:1   E265  block comment should start with '# '
55:30  E261  at least two spaces before inline comment
57:38  E261  at least two spaces before inline comment
59:1   E302  expected 2 blank lines, found 1
85:30  E211  whitespace before '('
91:28  E211  whitespace before '('
92:0   E272  multiple spaces before keyword
119:24 E211  whitespace before '('
133:16 E221  multiple spaces before operator
165:16 E221  multiple spaces before operator
188:80 E501  line too long (90 > 79 characters)
191:18 E211  whitespace before '('
212:1  E302  expected 2 blank lines, found 1
216:74 W291  trailing whitespace
225:23 E203  whitespace before ':'
225:30 E211  whitespace before '('
230:13 E265  block comment should start with '# '
234:17 E127  continuation line over-indented for visual indent
237:32 E203  whitespace before ':'
238:37 E203  whitespace before ':'
240:31 E203  whitespace before ':'
265:13 E265  block comment should start with '# '
266:13 E265  block comment should start with '# '
272:9  E265  block comment should start with '# '
273:9  E265  block comment should start with '# '
274:9  E265  block comment should start with '# '
277:1  E302  expected 2 blank lines, found 1
293:16 E225  missing whitespace around operator
298:16 E225  missing whitespace around operator
303:46 W291  trailing whitespace
386:15 E225  missing whitespace around operator
396:27 E127  continuation line over-indented for visual indent
397:27 E127  continuation line over-indented for visual indent
```

**Ceiling for the fix task (#2): the fixed `Asn1scc.py` must produce ≤ 33 flake8 issues — must not add new ones.** (The post-fix verifier must use the same shim, since stock flake8 cannot run at all on this host.)

---

## 6. Performance baseline — PROJECT_CACHE cold vs warm

Method: `time` via Python `subprocess` wall-clock (no `/usr/bin/time` binary on host); 3 repetitions each, median reported. Command per model (cwd = model dir):

```
PROJECT_CACHE=<cache_dir> opengeode <model>.pr system_structure.pr --check
```

(Models: `tests/testsuite/test1` → `og.pr`, `tests/testsuite/test-operators` → `operators.pr`; both also have `system_structure.pr`. Note: `--check` invokes `parse_asn1` with `pretty_print=True` — the cache stores `.py` + `.html`.)

### 6.1 Timings (seconds, wall clock)

| Model | COLD (fresh cache) ×3 | COLD median | WARM (populated cache) ×3 | WARM median | Speedup |
|---|---|---|---|---|---|
| test1 | 2.364 / 2.350 / 2.297 | **2.350** | 0.628 / 0.637 / 0.634 | **0.634** | 3.7× |
| test-operators | 2.321 / 2.304 / 2.334 | **2.321** | 0.584 / 0.589 / 0.590 | **0.589** | 3.9× |

### 6.2 asn1scc standalone (dominates the cold path)

| Model | asn1scc alone ×3 | median |
|---|---|---|
| test1 (`dataview-uniq.asn`) | 1.683 / 1.685 / 1.674 | **1.683 s** |
| test-operators (`dataview-uniq.asn`) | 1.730 / 1.741 / 1.716 | **1.730 s** |

Exact asn1scc invocation (as logged by `--debug`, test1):

```
asn1scc -customStgAstVersion 4 --field-prefix AUTO \
  -customStg /home/taste/tool-inst/share/asn1scc/python.stg::<cache>/54f589e7087b89d2e602290554258498.py \
  -renamePolicy 0 \
  -customIcdUper <cache>/pretty_print_asn1.stg::<cache>/54f589e7087b89d2e602290554258498.html \
  /home/taste/workspace/opengeode/tests/testsuite/test1/dataview-uniq.asn
```

### 6.3 Warm-hit proof (asn1scc skipped)

The log line **`[INFO] Reusing cached ASN.1 modules from <cache>/<md5>.py` DOES appear on every warm run** (grep count = 1 per run, both models):

```
[INFO] Reusing cached ASN.1 modules from /tmp/ogperf/warm_test1/54f589e7087b89d2e602290554258498.py
[INFO] Reusing cached ASN.1 modules from /tmp/ogperf/warm_test-operators/3e0a46358b1cad737e10b9197968a959.py
```

Corroborated by the timing delta: cold − warm ≈ 1.7 s ≈ exactly the standalone asn1scc time. **Post-fix guard: the same log line must appear and the warm/cold gap must stay ≈ asn1scc standalone time (plan threshold: investigate >20% warm-median regression).**

### 6.4 Cache dir content after cold run (current format)

```
<cache>/<md5>.py       # ASN.1 AST module (importlib-imported by bare md5 name — the V1/V2 surface)
<cache>/<md5>.html     # pretty-printed types (V9 surface)
<cache>/pretty_print_asn1.stg
<cache>/__pycache__/
```

Default cache perms observed: files 0644, dir 0755 (mkdir default umask) — the V8 finding.

---

## 7. Post-fix diff checklist (for task #5)

1. Re-run §2 table commands (note `test-c` must be run as `cd tests/testsuite && make test-c` — root Makefile lacks the target). Compare: test-parse **125/0**, test-ada **125/1 (only test-aggregation2)**, test-c **125/0**, test-rust **125/0 with 6 expected**. Any other failure = regression caused by the fix.
2. Re-run §3 pytest: **18 passed, 1 error (qtbot)**. New tests from task #3 add to the passed count; the qtbot error must remain the only error.
3. Re-run §5 flake8 (same shim): **≤ 33 issues**.
4. Re-run §6 timings: warm medians within 20% of **0.634 s** (test1) / **0.589 s** (test-operators); cold within 20% of **2.350 s** / **2.321 s**; "Reusing cached ASN.1 modules from" line still present on warm runs; new expected behaviour: old-format `{md5}.py` entries without a manifest are treated as a MISS (regenerated under sha256 name).
5. **Reinstall first** (§1.1): `make install` or PYTHONPATH pointing at the repo, else the fix isn't exercised.
6. V10 requires no action (already fixed; docs task corrects the audit report only).

---

*Baseline captured by plan task #1 (`baseline`). All raw logs: `/tmp/suite_test-{parse,ada,c,rust}.log`, `/tmp/pytest_baseline.log`, `/tmp/flake8_asn1scc_baseline.txt`, `/tmp/perf_*`.*
