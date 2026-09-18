# Security Audit — OpenGEODE ASN.1 Cache (`opengeode/Asn1scc.py`)

**Scope:** the MD5-based caching and `importlib` reloading of the ASN.1-generated
Python modules (`parse_asn1`, `asn2dataModel`), plus a sweep of the wider
codebase for related issues.
**Method:** source review + 5 working proofs of concept executed against the
then-current tree.
**Overall (at audit time):** the cache turns "open a model" into "execute whatever Python file
happens to be at a predictable path". Several findings are exploitable with
realistic preconditions.

> **Remediation update (2026-09-18).** All findings below have since been
> remediated in `opengeode/Asn1scc.py` — except **V10**, which re-verification
> showed to be *already fixed* in tree at audit time (the original claim was
> stale; see the correction in the V10 section), and **V11**, accepted as a
> documented local trust assumption. The findings, PoCs and severity
> assessments are preserved unchanged below as the historical record of the
> pre-fix tree (commit `10a6d195`); line numbers in the original prose refer to
> that tree. Each finding now carries a **Remediation (as built)** block with
> the verified post-fix line references and the residual risk, and the
> findings table carries a status column. The as-built architecture, threat
> model and maintenance guidance are documented in
> `docs/security-hardening-asn1scc-cache.md`; the pre-fix reference state in
> `docs/security-fix-baseline.md`; the post-fix regression/performance results
> in `docs/security-fix-verification-report.md`.

---

## How the mechanism worked, pre-fix (attack-relevant facts)

*Historical: this section and its line numbers describe the pre-fix tree
(`10a6d195`). The as-built mechanism is documented in
`docs/security-hardening-asn1scc-cache.md`.*

```
open .pr model (GUI, --check, --toAda, --toRust, ...)
  └─ ogParser.set_global_DV(asn1_files)         ogParser.py:374
       └─ Asn1scc.parse_asn1(files)             Asn1scc.py:74
            ├─ key = md5(contents of each ASN.1 file, sorted)   line 97-101
            ├─ name = prefix + key.hexdigest()   line 120-131
            │    prefix ∈ {"", "c_", "rust_"} from sys.argv
            ├─ if PROJECT_CACHE set and {name}.py and {name}.html exist:
            │      SKIP asn1scc entirely                        line 169-170
            └─ ast = importlib.import_module(name)              line 200
                 (module name is a bare md5 hex string; sys.path got outdir
                  APPENDED at line 147)
```

- The cached `.py` is **plain Python** (`type(...)` calls — see asn1scc's
  `python.stg`), imported with full privileges of the opengeode process.
- The key covers **only file contents**. File paths (line 117, commented out),
  `rename_policy`, `ast_version`, `extraflags`, `pretty_print` are **not**
  hashed; only the coarse `--toC`/`--toRust` argv prefix distinguishes them.

---

## Findings

| # | Finding | Severity | Preconditions | Status (2026-09-18) |
|---|---------|----------|---------------|--------------------|
| V1 | Cache poisoning → arbitrary code execution | **Critical** | Write access to `PROJECT_CACHE` dir | **FIXED** — manifest + ownership/mode/symlink + sha256 checks, forged `__pycache__` ignored; remediation pass also closed the generation (miss) path: stale entry removed, artifacts pre-created 0600, content read back through those very descriptors |
| V2 | Module shadowing from project dir (no cache involved) | **Critical** | Victim opens a model from attacker-influenced dir | **FIXED** — import strictly by path, `sys.path` no longer used in `parse_asn1` |
| V3 | Options not part of cache key (silent AST reuse) | Medium | Two runs differing in rename_policy/ast_version | **FIXED** — all effective options hashed into key and re-checked via manifest; remediation pass made the key encoding collision-free (count + per-file digests) |
| V4 | `-g` debug cache `./debug` in CWD | High | Debug flag + writable CWD | **FIXED** — same checks apply to `./debug`; dir created 0o700 |
| V5 | Argument injection into `asn1scc` via `-`-prefixed filename | Medium | Attacker controls an ASN.1 filename (USE clause/CIF) | **FIXED** — input validation, `TypeError` |
| V6 | MD5 content-only key (collision) | Low | Chosen-prefix collision effort | **FIXED** — sha256, self-delimiting count+digest encoding |
| V7 | `asn2dataModel`: `sys.path.insert(0, tempdir)` + stale tempdir | Medium | Reuse of a temp dir across projects | **FIXED** — `finally` sys.path restore, by-path imports, content-hash staleness, `atexit` cleanup, `ASN2DM` keyed by content |
| V8 | Cache dir created 0755, world-readable | Low | Default umask | **FIXED** — `mode=0o700` on creation, write bits stripped on new files, one-time warning on shared-writable dirs |
| V9 | HTML from cache rendered in GUI `QTextBrowser` | Low | Same as V1 | **MITIGATED** — html covered by manifest integrity + strict UTF-8 read; `QTextBrowser` already blocks JS |
| V10 | `NamedTemporaryFile(delete=False)` never removed | Low | GUI ASN.1 editor use | **VERIFIED-ALREADY-FIXED** — `finally: os.remove` at `opengeode.py:3940-3942` (original claim stale, see correction) |
| V11 | PATH lookup for `asn1scc`/`asn2dataModel`/`cat`/`make` | Info | Attacker controls PATH (pre-existing assumption) | **ACCEPTED** — standard local trust assumption, documented residual risk |

### V1 — Cache poisoning → arbitrary code execution (Critical)

`Asn1scc.py:169-170` trusts `{md5}.py`/`{md5}.html` **existence only**:
no integrity check, no ownership check, no freshness check against the inputs.
Anyone who can write into the cache dir plants a module that runs with the
victim's privileges the next time anyone parses matching ASN.1 content.

**PoC (executed, works end-to-end):**
```bash
# 1. compute the key of the victim's dataview
$ md5sum dataview-uniq.asn
54f589e7087b89d2e602290554258498  dataview-uniq.asn

# 2. plant BOTH files (line 169 requires .py AND .html when pretty_print=True)
$ cat > evil_cache/54f589...8498.py << 'EOF'
import os
open("/tmp/PWNED", "w").write("exec pid=%d" % os.getpid())
class types: pass; asn1Files = []; html = ''
EOF
$ echo '<html></html>' > evil_cache/54f589...8498.html

# 3. victim opens any model referencing that dataview
$ PROJECT_CACHE=evil_cache opengeode og.pr system_structure.pr --check
[INFO] Reusing cached ASN.1 modules from .../54f589....py
!!! PWNED: poisoned cache module executed ...
$ cat /tmp/PWNED
Arbitrary code exec via PROJECT_CACHE, pid=424112
```

**Impact:** full RCE as the victim (GUI process or CI build job).
**Realistic scenarios:**
- `PROJECT_CACHE` is an env contract with the TASTE/kazoo build system; shared
  CI runners often point it at one shared directory.
- Multi-user machines where the dir is group-writable.
**Fix (minimal):** validate the cached module before import — e.g. store the
exact asn1scc command line + file hashes + `mtime`+`uid` of inputs in a
sidecar file, or make the key a keyed hash (see V6 fix) and verify a stored
HMAC of the generated `.py` content. Refuse cache hits whose file is not
owned by the current user, or whose mtime predates the newest input.

**Remediation (as built).** A cache entry is now a *triple*
`{prefix}{sha256}.py` / `.html` / `.manifest`. The entry is only reused when
`_check_cache` (`Asn1scc.py:291-338`) passes **every** check: the manifest
parses as JSON (`:309`), the recorded options match the current options
(`:314`), the recorded asn1scc fingerprint matches the binary that is about
to run (`:317`, `_tool_fingerprint` `:130-140`), the recorded per-input
content hashes match (`:318-326`), and the sha256 of the actual artifact
bytes matches the manifest (`:330`, `:332-334`). Each file is additionally
vetted by `_verify_cached_artifact` (`:178-206`): not a symbolic link
(`:191`); on POSIX, owned by the current uid (`:197`) and not group- or
world-writable (`:200`) — checked and read through one and the same open
descriptor, so no swap can slip between check and read. Any failure logs the
reason (`Not reusing the ASN.1 cache entry: …`, `:533-534`) and
**regenerates** — the cache never crashes and never refuses to work.

**Remediation (remediation pass, generation window).** The reviewer found
that these checks only guarded the *hit* path: on a miss, the bytes read
after a regeneration were executed without any check, so an attacker with
write access to a shared cache folder could pre-create a 0666 artifact and
rewrite it during the ~1.7 s compile. The miss path is now hardened too
(`Asn1scc.py:552-611`): the stale entry is unlinked first
(`_remove_stale_cache_entry`, `:208-224` — a clear `TypeError` if it cannot
be removed), the artifacts are pre-created 0600 by this process
(`_precreate_cache_artifacts`, `:258-288`), and the generated content is read
back **from those very descriptors** (`_read_generated_artifact`,
`:227-256`) — a file replaced at the path during the generation (even one
recycling the same inode number) can never be the bytes that are executed.
Empty artifacts are refused.

The verified bytes are then executed with `compile()` + `exec()` by
`_import_module_from_source` (`:380-406`, called at `:634`) — *not*
`spec.loader.exec_module` — so a forged `__pycache__/<name>.pyc` planted next
to the artifact is never honoured (`exec_module` would both use and write
such a file; verified on Python 3.13). Old md5-named entries miss
automatically (different filename, no manifest) and are left untouched on
disk.

**Residual risk:** an attacker with the *same uid* as the victim (or root)
can rewrite artifact + manifest consistently — out of threat model (that
attacker can already modify the victim's own files); the manifest is an
integrity check against *other* users, not a keyed signature. The same-uid
attacker can likewise rewrite through the live pre-created artifact
descriptor during the generation window — the descriptor binding protects
against *other users*, not against the user's own compromised processes.
A first run after an asn1scc upgrade regenerates once (fingerprint `size`/
`mtime` change). A multi-uid *shared* cache folder no longer works as a
cache: every user rejects and regenerates the others' entries (group-
writable) or stops with a clear `TypeError` when the stale artifact cannot
be unlinked (sticky folder) — `PROJECT_CACHE` must be per-uid now. See
V9 for the html half of the entry.

### V2 — Module shadowing from the project directory (Critical)

Even **without any cache directory**, the imported module name is a bare
`md5` hex string, and `sys.path.append(outdir)` (line 147) puts the fresh
temp dir **last**. Python searches the current directory first, so a
`{md5}.py` planted in the project directory shadows the legitimately
generated one.

**PoC (executed):** with a clean environment (no `PROJECT_CACHE`), a planted
`54f589...8498.py` next to the model was imported instead of the module that
asn1scc had just generated in `/tmp/OG_ASN1SCC_*`:
```
!!! PWNED via CWD shadowing (no cache dir involved) !!!
```

**Impact:** opening a model from an attacker-influenced directory (cloned
repo, shared folder, extracted archive containing a stray `*.py` named after
any md5 of *any* ASN.1 content the victim also uses) executes attacker code.
The attacker doesn't even need the victim's exact dataview hash to match the
one they planted — they only need *some* plausible ASN.1 file plus its
matching planted module in the same directory, which is trivial for their own
model, and any victim opening their project dir model is hit.
**Fix:** import the generated file by **path**, not by module name:
`importlib.util.spec_from_file_location` / `module_from_spec` +
`spec.loader.exec_module`, avoiding `sys.path` entirely.

**Remediation (as built).** `sys.path.append(outdir)` is gone entirely from
`parse_asn1`. The generated module is imported by path from the generation/
cache folder via `_import_module_from_source` (`Asn1scc.py:380-406`, called
at `:634`), and the bytes that are executed are the *verified* bytes read by
`_check_cache` / `_read_generated_artifact` (`:589-610`) — there is no second
read from disk between verification and execution. `sys.path` is never
consulted for the cache artifact, so a `{hash}.py` planted in the model
directory (or anywhere on the path) is never imported. Verified post-fix: the
planted CWD-module PoC is no longer executed.

**Residual risk:** none specific to the import channel. The generated AST
is, by design, Python code that is executed — the hardening guarantees
*which* bytes are executed, not whether Python runs (the bytes are asn1scc's
output, hash-pinned to the manifest). One maintenance caveat: if a future
asn1scc `python.stg` emits `import` statements into the generated module,
those would resolve via `sys.path` (today's generated modules import
nothing — verified); the hardening doc §3.4 records the rule to apply if
that ever happens.

### V3 — Options not part of the cache key (Medium)

`rename_policy`, `ast_version`, `extraflags`, `pretty_print` are not hashed;
only the `--toC`/`--toRust` argv prefix distinguishes variants. In-memory
`AST[new_hash]` (line 136) and on-disk cache therefore silently return the
**wrong AST** for subsequent calls with different options.

**PoC (executed):** two consecutive `parse_asn1` calls with
`rename_policy=NoRename` vs `SystematicRenameAllEnumerants` returned the
**same module object** (`id()` identical); asn1scc was never re-invoked; the
C-backend rename policy was ignored.

**Impact:** wrong enum names → broken generated code (the exact failure mode
described in the code's own comment at lines 102-117). Also an integrity
issue: a first process "poisons" the shared cache for a differently-configured
second process.
**Fix:** fold all effective options into the hash (the comment at line 115
already suggests hashing the command line).

**Remediation (as built).** `_effective_options` (`Asn1scc.py:118-128`)
reduces the options to a JSON-serializable object
`{ast_version, rename_policy, flags (sorted values), extraflags,
pretty_print}`; its `repr()` is folded into the key hash (`:485`), and the
same object is stored in the manifest and re-compared verbatim on every hit
(`:314`). The in-memory `AST` dict is keyed by the same full key
(`:489-491`), so repeated in-process calls with different options now return
different modules. Verified post-fix: `NoRename` vs
`SystematicRenameAllEnumerants` produce different keys, different module
objects and a fresh asn1scc invocation; identical options still reuse the
same object.

**Remediation (remediation pass).** The reviewer also found that the
intermediate key encoding (each file's length prefixed before its raw
content) was not self-delimiting: a 12-byte file `"3456789012ab"` hashed
exactly like the three files `"2"`/`"456"`/`"89012ab"` — same key, so
the in-memory fast path (which never consults the manifest) would return
the first set's AST to the second. The key now hashes the file *count* and
each file's sha256 *digest* (`:481-484`) — a self-delimiting encoding that
cannot alias input sets (the digests are computed once anyway for the
manifest, so there is no extra I/O). `asn2dataModel`'s `ASN2DM` key got the
same treatment (`:807-812`); its raw-concatenation key aliased
`["ab","c"]` with `["a","bc"]`).

**Residual risk:** an option that does not influence the generated AST
still forces a separate cache entry (a cache miss) — a performance cost,
not a security issue. Conversely, any *future* option added to `parse_asn1`
must be added to `_effective_options` or V3 returns (maintenance note in
`docs/security-hardening-asn1scc-cache.md`).

### V4 — `-g` debug cache in CWD (High)

With `-g`, `PROJECT_CACHE=./debug` (line 81-82) — a **project-local**
directory subject to the same poisoning as V1, with the added twist that it's
committed to developer trees and CI scripts. Verified: planted module
executed via `--check -g`.

**Remediation (as built).** `-g` still sets `PROJECT_CACHE='./debug'
(`Asn1scc.py:421-422`), but the directory is created with `mode=0o700`
(`:431`) and every entry in it goes through the *same* manifest /
ownership / hash checks as any other cache folder — the cache code path does
not special-case `./debug` (`_check_cache` is called at `:523-529` whenever
`PROJECT_CACHE` is set). `asn2dataModel`'s own `./debug` folder is likewise
created `0o700` (`:833-835`). Verified post-fix (and now covered by the
regression test `test_debug_cache_poisoning_rejected`): a planted module in
`./debug` is regenerated, not executed.

**Residual risk:** a `./debug` directory that already exists (e.g. committed
to a repo with loose permissions) keeps its permissions — it is never
chmod'ed by opengeode (existing/foreign files are never modified, see V8) —
but its entries are still individually verified before use, so a poisoned
entry there is detected rather than executed.

### V5 — Argument injection into `asn1scc` (Medium)

ASN.1 filenames come from the model (`USE` clauses / CIF `ASNFilename`
annotations) and are appended to the asn1scc argument list **unquoted and
unchecked**. A filename starting with `-` is parsed by asn1scc as an option.

**PoC (executed):** `ASNFilename '-typePrefix'` in `system_structure.pr` →
asn1scc received `-typePrefix` as an option:
```
[DEBUG] ... -renamePolicy 0 -typePrefix
ASN.1 Compiler error ... 'argument -typePrefix must be followed by <prefix>'
```
Other asn1scc options (e.g. output paths for `-c`/`-Ada`/`-Rust` code
generation targets) could redirect generated code. Within opengeode the
filenames are usually co-located with the model, so exploitability is
contextual, but the parser should defend anyway.
**Fix:** pass file arguments after a `--` separator if supported, or reject
filenames beginning with `-`.

**Remediation (as built).** `_validate_input_files` (`Asn1scc.py:92-102`)
rejects any input whose name starts with `-` (`:97-100`) or is not an
existing file (`:101-102`), raising `TypeError` — the exception type
`ogParser.set_global_DV` (`ogParser.py:392-394`) converts to
`"ASN.1 compiler failed - …"`. It is applied at the boundary of **both**
APIs: `parse_asn1` (`:456`) and `asn2dataModel` (`:797`), before any file is
read or handed to `cat`, `asn1scc`, `asn2dataModel` or `make`. All external
tools are invoked via `QProcess` with list arguments (no shell), so there is
no shell-metacharacter channel either.

**Residual risk:** none known. A *directory* named like an ASN.1 file is
rejected by `os.path.isfile`; a file that exists but is unreadable fails at
`_read_input_files` (`:105-115`) with a `TypeError`.

### V6 — MD5, content-only (Low)

The key is a bare content MD5. MD5 collisions are cheap today
(chosen-prefix ≈ seconds on GPU/cloud). Two different dataviews with the same
MD5 → the second silently reuses the first's AST. Low likelihood for
accidental collisions, but trivially exploitable by a *determined* attacker
who wants a target's cache slot. Using `sha256` costs nothing and removes the
class; better, use `hashlib.sha256(frozenset(options) + contents)` and/or a
keyed hash.

**Remediation (as built).** The key and every hash in the manifest are now
sha256 (`Asn1scc.py:477-487` for the key, `:617-625` for the artifact hashes,
`:330`/`:332-334` for verification). The key hashes the file *count* and
each file's sha256 digest (`:481-484`) — a self-delimiting encoding, so two
different *sets* of inputs can never produce the same digest (the
intermediate length+content encoding was not self-delimiting and was
replaced in the remediation pass; see V3). Old md5-named entries simply
never match the new (longer) key and are ignored.

**Residual risk:** none considered realistic (sha256 chosen-prefix attacks
are not feasible); the practical threat was substitution, not collision,
and that is covered by the manifest (V1).

### V7 — `asn2dataModel` temp dir + `sys.path.insert(0)` (Medium)

`asn2dataModel` (lines 277-389) creates `tempfile.mkdtemp()` — **never
removed** (leak of generated `.so`/`.py`), inserts it at **the front** of
`sys.path` (line 299) and then imports `Stubs`, `db_model`,
`og_dataview_asn` by bare name, with `importlib.reload` on repeated calls.
The staleness check (line 308-322, mtime vs ctime) can leave a stale
concatenated `.asn` in place (mtime granularity, ctime semantics on
different filesystems). On a shared temp (`/tmp` is sticky-bit, but the dir
itself is user-owned) this is mostly a **correctness/leak** issue, but the
bare-name imports are the same shadowing pattern as V2 if any same-named
module exists earlier on the path.
**Fix:** import by path (V2 fix), `shutil.rmtree` the tempdir in a
`finally`, and key on content hash instead of timestamps.

**Remediation (as built).** `asn2dataModel` (`Asn1scc.py:782-925`) was
reworked:

- **`sys.path` is restored in a `finally`** (`:905-913`) — also when `cat`,
  `asn2dataModel` or `make` fail, and even if a third party mutated
  `sys.path` during the window (the `finally` removes `tempdir` wherever it
  sits).
- **All five generated modules are imported by path**, in dependency order
  `DV_Types → Stubs → DV → og_dataview_asn → db_model`, each registered in
  `sys.modules` under its own name so the generated code's bare
  `import DV` / `from Stubs import …` resolve to the *current* folder's
  modules (`_import_dataview_modules` `:742-764`, `_register_sibling_modules`
  `:767-770`). `sys.path.insert(0, tempdir)` stays in place only for the
  duration of one call (`:848`, inserted just before the `try:` so the
  tempdir is at the *front* — for sibling modules opengeode does not know
  about) and is guaranteed removed by the same `finally`.
- **Staleness is content-based**: a sidecar `og_dataview.inputs.sha256` holds
  the key of the inputs the folder was generated from
  (`_dataview_key_file` `:715-719`, `_dataview_files_are_current`
  `:722-739`); the fragile mtime/ctime comparison is gone.
- **`ASN2DM` is keyed by count + per-file digests + `repr(outdir)`**
  (`:807-812`) — this also fixes the pre-existing correctness bug where a
  second call with different files reloaded and returned the *first*
  dataview, and the remediation pass removed the residual aliasing of its
  raw-concatenation key (`["ab","c"]` vs `["a","bc"]`).
- **Temp dirs are removed at process exit**: `mkdtemp` folders are registered
  and `atexit.register(shutil.rmtree, …, ignore_errors=True)`
  (`:836-839`); an explicit `outdir` is never removed; `-g` uses `./debug`
  (0o700) and is never registered.
- **Every generated module is verified before it is executed**
  (`_verify_cached_artifact(check_mode=False)` in `_import_dataview_modules`
  `:757-760` — not a symlink, owned by the current user), so even a
  caller-chosen shared `outdir` cannot serve foreign-planted modules to a
  second call (remediation pass; the reuse path previously trusted the
  sidecar key alone).
- Inputs are validated (`:797`) and read exactly once (`:798`); the concat
  file and the staleness sidecar are written through `_write_file_checked`
  (`:862-867` — `O_NOFOLLOW`, mode 0600), never through a symlink.

**Residual risk:** the temp dirs intentionally live for the whole process
(the generated `*_getset.so` and the module objects are used after the call
returns); they are 0700 `mkdtemp` directories owned by the user, so the
exposure is disk usage, not access. The generated DMT output is executed as
Python by design — trusting the local `asn2dataModel` toolchain is a local
trust assumption of the same class as V11. DMT modules in a caller-chosen
`outdir` are link/ownership-checked but not hash-bound (the DMT toolchain has
no manifest); no production caller in this tree passes a shared `outdir`.

### V8 — Cache directory permissions (Low)

`os.makedirs(project_cache)` (line 89) follows umask — 0755 by default,
world/group-readable. Generated ASTs of aerospace models may be sensitive.
Preconditioning for V1 on multi-user hosts (a 0777 cache is a free-for-all).
**Fix:** `os.makedirs(project_cache, mode=0o700)`.

**Remediation (as built).** The cache folder is created with `mode=0o700`
(`Asn1scc.py:431`); files written by a generation have their group/world
*write* bits stripped regardless of umask (`_harden_cache_file_perms`
`:142-157`, applied at `:629-632` — only on files this run just created,
never on existing/foreign files; the list now includes the pretty-print
template `pretty_print_asn1.stg`, which the remediation pass added). If an
*existing* cache folder is group- or world-writable, opengeode logs a one-time
warning (`_warn_if_shared_writable` `:159-175`, called at `:438`) and keeps
using it — shared TASTE cache folders must keep working; the per-file
ownership and mode checks from V1 are the actual protection there.
Additionally (remediation pass) an explicit `asn2dataModel` `outdir` is now
created `0o700` too (`:841`), closing the asymmetry with the other folders.

**Residual risk:** an existing shared cache folder stays as permissive as
its administrator left it (opengeode never chmod's directories it did not
create). Cache *files* remain as readable as the umask permits (typically
0644) — confidentiality of the cache content is not enforced beyond the
0700 default directory creation; the fix targets *integrity*. Note that a
shared, multi-uid cache folder no longer *works* as a cache under the V1
ownership checks — see V1's residual risk.

### V9 — Cached HTML rendered in GUI (Low)

`ast.html = open(html_filepath).read()` (line 207) →
`asn1_browser.setHtml(...)` (opengeode.py:3517-3518). Same write-access
precondition as V1, but `QTextBrowser` doesn't run JavaScript; residual risk
is injected links/contents (phishing/obfuscation). Fix alongside V1.

**Remediation (as built, status: MITIGATED).** The html file is now a
manifest-covered artifact: its sha256 is recorded at generation
(`Asn1scc.py:622-625`) and re-verified on every cache hit (`:332-334`),
through the same ownership/mode/symlink checks as the `.py` (the html is
passed through `_verify_cached_artifact` at `:304-307`, following the `.py`
at `:300-303`). It is read once, as part of the cache check (on a
generation, from the pre-created descriptor of §V1's remediation pass), and
decoded strictly as UTF-8 (`:640-646`, raising `TypeError` on invalid
UTF-8). `QTextBrowser` does not execute JavaScript (pre-existing Qt
property, unchanged).

**Residual risk:** crafted-but-*consistent* html (links, misleading text,
images with absolute URLs) can still be rendered — but making a consistent
manifest+artifact pair requires the same uid as the victim (out of threat
model, see V1).

### V10 — Temp ASN.1 file leak (Low)

`opengeode.py:3902`: `NamedTemporaryFile(..., delete=False)` writes the
ASN.1 editor's content to a world-readable temp file that is never deleted.
**Fix:** `delete=True` with a `finally` close, or unlink in `finally`.

> **Correction (verified 2026-09-18): status VERIFIED-ALREADY-FIXED.** The
> original claim was stale on both counts. (1) The file **is** removed: the
> creation at `opengeode.py:3902` is surrounded by a `try:` whose `finally:`
> block at **`opengeode.py:3940-3942`** does
> `if os.path.exists(tmp_file_path): os.remove(tmp_file_path)` — and every
> return path taken after the file is created (the early returns at `:3911`,
> `:3925`, `:3928`, the normal returns at `:3935`/`:3937`, and the `except`
> at `:3938`) is inside that `try`, so removal is guaranteed (the returns
> at `:3896`/`:3899-3900` precede the creation and cannot leak).
> (2) The file was never world-readable: `tempfile.NamedTemporaryFile`
> creates with `mkstemp` semantics, i.e. mode `0600` (verified on this host).
> This is the only `NamedTemporaryFile` site in the package (`grep -n
> NamedTemporaryFile opengeode/*.py`), and the installed site-packages copy
> carries the identical fixed code (confirmed in
> `docs/security-fix-baseline.md` §4). No code change was needed or made.

### V11 — PATH-based tool lookup (Info)

`spawn.find_executable('asn1scc' | 'asn2dataModel' | 'cat' | 'make')` trusts
PATH. A hostile PATH yields hostile binaries — but that is a standard local
trust assumption, listed for completeness.

**Remediation: ACCEPTED (documented residual risk).** No change: whoever
controls `PATH` can already run arbitrary code as the user, so hardening
the lookups would be cosmetic. The asn1scc binary that `find_executable`
resolves *is* fingerprinted into every cache manifest (`_tool_fingerprint`,
`Asn1scc.py:130-140`), so cache entries are at least pinned to the exact
binary (path/size/mtime) that produced them, and an entry generated by a
different binary is never reused.

---

## Things checked and found **not** vulnerable

- `eval` sites: `ogParser.py:8343` (`parseSingleElement` — guarded by an
  assert whitelist of symbol names), `AdaGenerator.py:2372` (constant folding
  of already-typed numeric literals), `genericSymbols.py:267` (internal
  class-name registry). All low risk.
- QProcess usage is list-args, no `shell=True` anywhere in the package.
- `Lander.py` randomness is the embedded mini-game.
- `.pr` parsing itself (ANTLR) does not `eval` model text.
- `mkdtemp()` is 0700 (verified) — the exposure is `makedirs` of the cache
  dir, not the temp dirs.

---

## Recommended hardening (summary, historical — implemented)

1. **Import by path, not by name** (fixes V1, V2, V7):
   `spec_from_file_location(new_hash, py_filepath)` — never `sys.path`.
2. **Make the cache key cover all inputs**: sha256 over contents **and**
   sorted paths **and** all options (`rename_policy`, `ast_version`,
   `extraflags`, `pretty_print`) (fixes V3, V6).
3. **Integrity check on cache hits**: verify a sidecar manifest
   (input hashes + asn1scc version + options) before trusting `{hash}.py`;
   re-generate on mismatch (fixes V1, V4).
4. **Reject dash-prefixed filenames** passed to asn1scc (fixes V5).
5. `os.makedirs(project_cache, mode=0o700)` (V8), `shutil.rmtree` temp dirs
   (V7), `delete=True` for the ASN.1 editor temp file (V10).

*As-built deviations from this sketch:* paths are deliberately **not**
hashed (2) — content-only keys are what make cross-project cache reuse
possible (a performance requirement; V3 is fixed by hashing the *options*
instead); the integrity manifest (3) additionally pins ownership and file
modes; the temp dirs of `asn2dataModel` (5) are removed at process exit via
`atexit`, not per call, because the generated modules outlive the call; and
V10 needed no change (already fixed, see correction above). The remediation
pass added a second wave of measures that the sketch did not cover: the
generation (miss) path never writes through a file this process does not
control (stale entry removed, artifacts pre-created 0600, content read back
from those very descriptors — kills the mid-generation replacement window);
all fixed-name writes in shared locations go through `O_NOFOLLOW`/`O_EXCL`
descriptors (no symlink can redirect them); and the cache keys use a
collision-free count+digest encoding. The full as-built design is in
`docs/security-hardening-asn1scc-cache.md`.

All five PoCs are reproducible from `/tmp/ogsec/poc{1..5}` with the commands
shown above (against the pre-fix tree). Post-fix, each PoC's payload must
*not* execute; the concrete expected post-fix behaviour is given in the
**Remediation (as built)** blocks above.

---

## Verification

How the remediation was and is tested:

- **Regression/security unit tests:** `tests/pytests/test_asn1scc_cache.py`
  (new) — cache key and option coverage (`rename_policy`, `ast_version`,
  `flags`, `extraflags`, input-set separation), manifest writing and
  verification, poisoned/symlinked/foreign-owned entry rejection,
  **generation-window attacks** (stale artifact not written through,
  mid-generation replacement not executed, unremovable entry ⇒ fail-safe
  `TypeError`), `-g`/`./debug` poisoning (V4), CWD-shadowing rejection,
  `-`-filename `TypeError`, `sys.path` restoration, cache-folder
  permissions. The pre-existing `tests/pytests/test_asn1scc.py`
  (asn2dataModel) must keep passing.
- **PoC re-runs:** the implementer re-executed the audit's PoCs (a)–(e)
  against the fixed tree — poisoned cache entries (with and without forged
  manifests, 666-mode files, symlinks, forged `__pycache__/*.pyc`, old md5
  names), CWD shadowing, option confusion, dash-filename injection, and the
  asn2dataModel tempdir/`sys.path` scenarios; every payload was neutralised.
  See the per-finding **Remediation (as built)** blocks for the expected
  outcome of each.
- **Full regression + performance verification:**
  `docs/security-fix-verification-report.md` records the post-fix run of the
  four make suites (`test-parse` / `test-ada` / `test-c` / `test-rust`), the
  full pytest, the flake8 count, and the cold/warm `PROJECT_CACHE` timings
  against the pre-fix reference values in `docs/security-fix-baseline.md`
  (§6: warm median 0.634 s for `test1`, 0.589 s for `test-operators`; the
  warm run must log `Reusing cached ASN.1 modules from …` and skip asn1scc
  entirely).
- **Environment note:** verification must run against the *repo* copy of
  opengeode (`PYTHONPATH=<repo>`, `make install`, or removal of the orphaned
  `site-packages/opengeode` copy) — see `docs/security-fix-baseline.md` §1.1;
  otherwise the stale installed copy is exercised instead.

The recipe to reproduce all of the above (commands, models, expected numbers)
is in `docs/security-hardening-asn1scc-cache.md` §"How to re-verify".
