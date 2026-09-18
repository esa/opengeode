#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security regression tests for the ASN.1 cache of opengeode/Asn1scc.py.

Each test below is a small, self-contained proof (an "executable PoC") of
one finding of the security audit of the ASN.1 cache (see
docs/security-audit-asn1scc-cache.md). Every security test:

  * FAILS on the vulnerable code that the audit describes, and
  * PASSES on the fixed code.

The two performance guards (in-memory reuse, warm cache) pass on both:
they make sure that the fix did not cost the speed of the cache.

The fixed behaviour under test (all in opengeode/Asn1scc.py):

  * parse_asn1 caches the generated AST in $PROJECT_CACHE under a file name
    built from a sha256 of the backend prefix, of the content of the input
    files (never of their paths, so that identical ASN.1 files of different
    projects share one entry) and of ALL the effective compiler options
    (ast_version, rename_policy, flags, extraflags, pretty_print).
  * A sidecar ".manifest" (JSON) is written LAST, next to the module; it
    records the options, a fingerprint of the asn1scc binary, the content
    hash of each input file and the hash of each generated artifact. A
    cached module is reused only if the manifest is present, parses,
    belongs to the current user, is not a symbolic link, is not group- or
    world-writable, and matches all the recorded hashes; otherwise the
    ASN.1 compiler is simply called again.
  * The generated module is imported by path from its verified content,
    never by name: sys.path is not used at all, so no file can shadow it.
  * The input files are validated (must exist, must not start with "-")
    before they are handed over to the external tools, raising TypeError.
  * asn2dataModel always restores sys.path (try/finally), imports the
    generated modules by path from the current output folder (a second
    call with different inputs returns the NEW dataview and does not
    mutate the first one), keys its cache by the content of the inputs,
    and creates cache folders with mode 0o700.

No test here touches the real cache of the user: PROJECT_CACHE is always
redirected to a temporary folder (or unset), and the in-memory caches of
the module (Asn1scc.AST, Asn1scc.ASN2DM) are cleared around each test.

These tests need the asn1scc, asn2dataModel, cat and make tools (like the
other tests of this folder, which call asn2dataModel unconditionally):

    cd tests/pytests
    PATH=~/.local/bin:$PATH PYTEST_QT_API=PySide6 python3 -m pytest -v \
        test_asn1scc_cache.py

Mapping of the tests to the audit findings:

  V1  cache poisoning -> RCE      test_cache_poisoning_rejected (no
                                  manifest / manifest hash mismatch),
                                  test_cache_poisoning_rejected_world_
                                  writable, test_cache_poisoning_rejected_
                                  symlink, test_old_md5_entry_ignored,
                                  test_manifest_written
                                  (remediation, generation window):
                                  test_generation_writes_through_own_file,
                                  test_generation_rejects_replaced_artifact,
                                  test_generation_failsafe_unremovable_entry
  V2  CWD shadowing               test_cwd_shadowing_rejected
  V3  options not in the key      test_cache_key_covers_options,
                                  test_cache_key_covers_ast_version,
                                  test_cache_key_covers_flags_and_extraflags,
                                  test_cache_key_separates_input_file_sets
  V4  debug cache ("-g")          test_debug_cache_poisoning_rejected
  V5  argument injection          test_dash_filename_rejected,
                                  test_dash_filename_rejected_
                                  asn2dataModel, test_missing_file_rejected
  V6  md5 key                     test_sha256_key
  V7  asn2dataModel               test_syspath_restored_after_
                                  asn2dataModel, test_asn2dataModel_failure_
                                  restores_syspath
  V8  cache folder permissions    test_cache_dir_created_0700
  V9  cached HTML                 test_html_tampering_detected
  perf no-regression              test_in_memory_cache_reuse,
                                  test_warm_cache_skips_compiler
  API no-regression              test_returned_ast_attributes
"""

import hashlib
import json
import logging
import os
import re
import stat
import sys

import pytest

from opengeode import Asn1scc
from opengeode.Asn1scc import ASN1, parse_asn1, asn2dataModel

# These tests verify the code of THIS repository: conftest.py inserts the
# repository root at the front of sys.path, so the imported module must be
# the one of the repository. A stale physical copy of the package in
# site-packages must never be tested silently; if the imported module is
# not the one of the repository (conftest missing, file copied elsewhere),
# it is accepted only when it is byte-identical to it (a normal
# "make install").
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
REPO_ASN1SCC = os.path.join(REPO_ROOT, 'opengeode', 'Asn1scc.py')
if os.path.realpath(Asn1scc.__file__) != os.path.realpath(REPO_ASN1SCC):
    with open(REPO_ASN1SCC, 'rb') as repo_source:
        repo_content = repo_source.read()
    with open(Asn1scc.__file__, 'rb') as imported_source:
        imported_content = imported_source.read()
    assert imported_content == repo_content, (
        f'These tests must exercise the Asn1scc.py of the repository '
        f'({REPO_ASN1SCC}), not a different copy of the package '
        f'({Asn1scc.__file__}): the security fixes under test would not '
        'be the code that runs.')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DV1 = os.path.join(DATA_DIR, 'dv1.asn')
DV2 = os.path.join(DATA_DIR, 'dv2.asn')

# Small ASN.1 data view used by most tests (nothing is written in the
# repository: the file is created in the temporary folder of each test)
TINY_ASN1 = '''\
Tiny-DV DEFINITIONS ::= BEGIN

-- A couple of types, enough for the ASN.1 compiler to generate an AST

   My-Bool ::= BOOLEAN
   My-Int  ::= INTEGER (0 .. 255)

END
'''
TINY_TYPES = ['My-Bool', 'My-Int']


def unique_tiny_asn1(tmp_path, tag):
    ''' Path of a small ASN.1 file whose content is unique to the calling
        test (a harmless ASN.1 comment makes it unique). Needed by the
        poisoning and shadowing tests: on the vulnerable code the cache
        key covered the content only, so two parses of the same content
        made different tests share one module name - and since the
        vulnerable code appended every output folder to sys.path, an
        import by name could then find the file of ANOTHER test and hide
        the planted payload, masking the vulnerability. With a content
        unique to the test, the planted payload is the only module with
        that name in the whole session. '''
    assert '\nEND\n' in TINY_ASN1
    path = tmp_path / f'dataview_{tag}.asn'
    path.write_text(TINY_ASN1.replace(
        '\nEND\n', f'\n-- Unique content of test "{tag}"\n\nEND\n'))
    return str(path)


# Source of the payload module "planted" by an attacker in the poisoning
# and shadowing tests. If a vulnerable implementation ever imports it, the
# marker file is created - the tests assert that it never happens.
POISON_PAYLOAD = (
    "POISONED = True\n"
    "with open({marker!r}, 'w') as _marker:\n"
    "    _marker.write('poisoned module executed')\n")


def make_poison_payload(marker_path):
    ''' Source of a module that proves it was executed by writing a file '''
    return POISON_PAYLOAD.format(marker=str(marker_path))


def sha256_of(path):
    ''' sha256 of the content of a file '''
    with open(path, 'rb') as source:
        return hashlib.sha256(source.read()).hexdigest()


def cache_py(cache_dir, key):
    return os.path.join(cache_dir, key + '.py')


def cache_html(cache_dir, key):
    return os.path.join(cache_dir, key + '.html')


def cache_manifest(cache_dir, key):
    return os.path.join(cache_dir, key + '.manifest')


def py_files(cache_dir):
    ''' Paths of the ".py" files of a cache folder '''
    return [os.path.join(cache_dir, name)
            for name in os.listdir(cache_dir)
            if name.endswith('.py')]


def manifest_files(cache_dir):
    ''' Paths of the ".manifest" files of a cache folder '''
    return [os.path.join(cache_dir, name)
            for name in os.listdir(cache_dir)
            if name.endswith('.manifest')]


def plant_module(directory, key, marker_path):
    ''' Write, in the given folder, a payload module named after a cache
        key. If it is ever imported, the marker file is created. The
        module is also removed from sys.modules, so that even an import
        by name cannot be served from a previous import. '''
    payload_path = os.path.join(directory, key + '.py')
    with open(payload_path, 'w', encoding='utf-8') as source:
        source.write(make_poison_payload(marker_path))
    sys.modules.pop(key, None)
    return payload_path


def clear_in_memory_caches():
    ''' Reset the in-memory caches of the module, so that no test can
        influence another one through Asn1scc.AST / Asn1scc.ASN2DM '''
    Asn1scc.AST.clear()
    Asn1scc.ASN2DM.clear()
    for name in (getattr(Asn1scc, '_DMT_MODULES', None) or ()):
        sys.modules.pop(name, None)


def arm_asn1scc_lookup(monkeypatch):
    ''' Make any lookup of the asn1scc binary fail loudly: a lookup after
        this point proves that the parse was NOT served from the
        in-memory cache (parse_asn1 looks the binary up only after the
        in-memory cache was checked). Only valid to prove an IN-MEMORY
        cache hit: a warm on-disk hit legitimately looks the binary up,
        to fingerprint the compiler in the manifest check. '''
    real_find_executable = Asn1scc.spawn.find_executable

    def find_executable(name, *args, **kwargs):
        if name == 'asn1scc':
            raise AssertionError(
                'The ASN.1 compiler was looked up although the AST '
                'should have been reused from the in-memory cache')
        return real_find_executable(name, *args, **kwargs)

    monkeypatch.setattr(Asn1scc.spawn, 'find_executable', find_executable)


def arm_qprocess(monkeypatch, message):
    ''' Replace QProcess with a class whose start() fails loudly: an
        attempt to start an external tool proves that the code should
        have been rejected, or that a cache should have been reused. '''
    class Bomb(object):
        def __init__(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            raise AssertionError(message)

        def setWorkingDirectory(self, *args, **kwargs):
            pass

    monkeypatch.setattr(Asn1scc, 'QProcess', Bomb)


# -----------------------------------------------------------------------------
# Fixtures: isolation of the environment
# -----------------------------------------------------------------------------

@pytest.fixture
def project_cache(tmp_path):
    ''' The scratch cache folder of the test (never the real user cache) '''
    return str(tmp_path / 'project_cache')


@pytest.fixture(autouse=True)
def clean_sys_argv(monkeypatch):
    ''' A test must not be influenced by the command line of the process
        that runs it ("--toC" or "-g" in sys.argv changes the behavior of
        parse_asn1 and asn2dataModel) '''
    monkeypatch.setattr(sys, 'argv', ['opengeode'])


@pytest.fixture(autouse=True)
def isolated_cache_environment(monkeypatch, project_cache):
    ''' Redirect PROJECT_CACHE to a scratch folder and clear the in-memory
        caches before and after every test, so that:
        - no test can read or write the real cache of the user,
        - no test can be influenced by a previous one. '''
    monkeypatch.setenv('PROJECT_CACHE', project_cache)
    clear_in_memory_caches()
    yield
    clear_in_memory_caches()


@pytest.fixture
def no_project_cache(isolated_cache_environment, monkeypatch):
    ''' Environment without any on-disk cache (a user who never configured
        PROJECT_CACHE - the normal case when a model is opened from an
        arbitrary, possibly attacker-influenced folder). The dependency on
        the autouse fixture guarantees that PROJECT_CACHE is deleted
        after it was set, not before. '''
    monkeypatch.delenv('PROJECT_CACHE', raising=False)


@pytest.fixture
def tiny_asn1_file(tmp_path):
    ''' A small ASN.1 file created in the temporary folder of the test '''
    path = tmp_path / 'tiny.asn'
    path.write_text(TINY_ASN1)
    return str(path)


@pytest.fixture
def qprocess_bomb(monkeypatch):
    ''' QProcess.start fails loudly: an attempt to start an external tool
        proves that the input should have been rejected before '''
    arm_qprocess(monkeypatch,
                 'An external tool was started although the input file '
                 'should have been rejected first (argument injection '
                 'reached the tool)')


# -----------------------------------------------------------------------------
# V3 - the compiler options are part of the cache key
# -----------------------------------------------------------------------------

def test_cache_key_covers_options(project_cache, tiny_asn1_file):
    ''' V3: the same input files parsed with different options (here the
        rename policy) must not share the same cache entry: the second
        parse creates its own entry, and returns its own module.
        On the vulnerable code the key was a hash of the content only, so
        the second call silently returned the AST of the first call (same
        module object, ASN.1 compiler not re-invoked). '''
    first = parse_asn1([tiny_asn1_file], rename_policy=ASN1.NoRename)
    second = parse_asn1([tiny_asn1_file],
                        rename_policy=ASN1.SystematicRenameAllEnumerants)

    assert second is not first, (
        'The same input parsed with another rename policy returned the '
        'AST module of the first parse: the compiler options are not part '
        'of the cache key (audit finding V3)')
    assert second.__name__ != first.__name__, (
        'the two parses must have distinct cache keys')
    assert Asn1scc.AST[first.__name__] is first
    assert Asn1scc.AST[second.__name__] is second

    # Two distinct entries on the disk: the second parse produced a new
    # module file in the cache folder
    assert os.path.isfile(cache_py(project_cache, first.__name__))
    assert os.path.isfile(cache_py(project_cache, second.__name__)), (
        'the parse with the other rename policy did not create a new '
        'cache entry (V3)')


def test_cache_key_covers_ast_version(project_cache, tiny_asn1_file):
    ''' V3 (other option): the ast_version option is part of the key too '''
    first = parse_asn1([tiny_asn1_file],
                       ast_version=ASN1.NoParameterizedTypes)
    second = parse_asn1([tiny_asn1_file],
                        ast_version=ASN1.UniqueEnumeratedNames)
    assert second is not first, (
        'the same input parsed with another ast_version returned the AST '
        'of the first parse (V3)')
    assert second.__name__ != first.__name__
    assert os.path.isfile(cache_py(project_cache, first.__name__))
    assert os.path.isfile(cache_py(project_cache, second.__name__))


def test_cache_key_covers_flags_and_extraflags(project_cache, tmp_path):
    ''' V3 (remaining options): the flags and the extraflags are part of the
        key too: a parse with other flags or extra compiler options must
        never reuse the AST of another parse.
        (--slim is a real option of asn1scc that changes nothing here; the
        point is only that two different option sets give two entries.) '''
    asn1_file = unique_tiny_asn1(tmp_path, 'flags_extraflags')

    plain = parse_asn1([asn1_file])
    other_flags = parse_asn1([asn1_file], flags=[ASN1.NoInnerTypes])
    assert other_flags.__name__ != plain.__name__, (
        'a parse with other flags reused the cache entry of the plain parse '
        '(V3: the flags are not part of the cache key)')
    assert os.path.isfile(cache_py(project_cache, other_flags.__name__))

    with_extra = parse_asn1([asn1_file], extraflags=['--slim'])
    assert with_extra.__name__ != plain.__name__, (
        'a parse with extra compiler options reused the cache entry of the '
        'plain parse (V3: the extraflags are not part of the cache key)')
    assert with_extra.__name__ != other_flags.__name__
    assert os.path.isfile(cache_py(project_cache, with_extra.__name__))
    # The parse with the extra option still produces a proper AST
    assert sorted(with_extra.types) == TINY_TYPES


def test_cache_key_separates_input_file_sets(project_cache, tmp_path):
    ''' V3/V6 support: two DIFFERENT sets of input files whose contents
        concatenate to the same bytes must never share a cache entry
        (the key must identify the set of inputs, not the concatenation).
        This is the property that the count-and-digest encoding guarantees
        in general; the test guards it against the encodings that alias
        such sets (a plain concatenation of the contents, as the original
        code and the asn2dataModel key did). The exact numeric collision
        of the intermediate "length+content" encoding (a 12-byte file
        hashing like three files "2"/"456"/"89012ab") needs file contents
        that start with bare digits, which the ASN.1 compiler rejects, so
        it cannot be reproduced with parseable files - it is documented in
        docs/security-hardening-asn1scc-cache.md instead. '''
    # One file holding two complete modules...
    both = tmp_path / 'both.asn'
    both.write_text('Set1-DV DEFINITIONS ::= BEGIN\n'
                    '   A ::= BOOLEAN\n'
                    'END\n'
                    'Set2-DV DEFINITIONS ::= BEGIN\n'
                    '   B ::= BOOLEAN\n'
                    'END\n')
    # ...or the very same text split at a module boundary into two files
    part_one = tmp_path / 'part_one.asn'
    part_one.write_text('Set1-DV DEFINITIONS ::= BEGIN\n'
                        '   A ::= BOOLEAN\n'
                        'END\n')
    part_two = tmp_path / 'part_two.asn'
    part_two.write_text('Set2-DV DEFINITIONS ::= BEGIN\n'
                        '   B ::= BOOLEAN\n'
                        'END\n')
    assert part_one.read_text() + part_two.read_text() == both.read_text()

    one_file = parse_asn1([str(both)])
    two_files = parse_asn1([str(part_one), str(part_two)])
    assert two_files.__name__ != one_file.__name__, (
        'two different sets of input files produced the same cache key: '
        'the key does not identify the inputs (key encoding collision)')
    # Both parses generated their own entry
    assert os.path.isfile(cache_py(project_cache, one_file.__name__))
    assert os.path.isfile(cache_py(project_cache, two_files.__name__))
    # The same types, but two distinct ASTs: one parse must never silently
    # reuse the AST of another parse
    assert sorted(two_files.types) == sorted(one_file.types) == ['A', 'B']


# -----------------------------------------------------------------------------
# V6 - sha256 (not md5) cache keys
# -----------------------------------------------------------------------------

def test_sha256_key(project_cache, tiny_asn1_file, monkeypatch):
    ''' V6: the cache file names are the backend prefix (optional) followed
        by 64 hexadecimal digits (sha256), not 32 (md5), and no 32-hex
        ".py" file is created anymore. '''
    pattern = re.compile(r'^(c_|rust_)?[0-9a-f]{64}$')

    ast = parse_asn1([tiny_asn1_file])
    assert pattern.match(ast.__name__), (
        f'the cache key must be a sha256 (64 hex digits), found '
        f'"{ast.__name__}" (V6)')
    assert os.path.isfile(cache_py(project_cache, ast.__name__))

    # With the C backend option, the key carries the "c_" prefix
    monkeypatch.setattr(sys, 'argv', ['opengeode', '--toC'])
    ast_c = parse_asn1([tiny_asn1_file])
    assert pattern.match(ast_c.__name__), (
        f'the cache key of the C backend must be "c_" + 64 hex digits, '
        f'found "{ast_c.__name__}" (V6)')

    # No md5-named module is created anymore
    for path in py_files(project_cache):
        stem = os.path.basename(path)[:-3]
        assert not re.fullmatch(r'(c_|rust_)?[0-9a-f]{32}', stem), (
            f'the cache still contains a 32-hex (md5) module: '
            f'"{os.path.basename(path)}" (V6)')


# -----------------------------------------------------------------------------
# V1 - a poisoned cache entry is never executed
# -----------------------------------------------------------------------------

def test_cache_poisoning_rejected(project_cache, tmp_path, caplog):
    ''' V1: a payload module written over a cache entry is never executed
        and never returned. The module must be regenerated instead.
        Cases:
        (a) the manifest is missing (interrupted generation, or removed):
            the entry is not trusted, it is regenerated;
        (b) the manifest is present but the recorded hash of the module
            does not match its content: the entry is regenerated.
        On the vulnerable code the cached module was imported when both
        the ".py" and the ".html" files existed, without any check: the
        payload was executed (arbitrary code execution). pretty_print=True
        is used here, like the real caller (ogParser.set_global_DV), so
        that both artifacts exist. '''
    caplog.set_level(logging.INFO, logger='opengeode.Asn1scc')
    asn1_file = unique_tiny_asn1(tmp_path, 'cache_poisoning')

    # Cold parse: build the key and a healthy cache entry
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__
    assert os.path.isfile(cache_py(project_cache, key))
    assert os.path.isfile(cache_html(project_cache, key))

    # (a) The manifest is missing
    marker_a = tmp_path / 'poison_executed_case_a.marker'
    if os.path.exists(cache_manifest(project_cache, key)):
        os.remove(cache_manifest(project_cache, key))
    plant_module(project_cache, key, marker_a)
    clear_in_memory_caches()

    second = parse_asn1([asn1_file], pretty_print=True)

    assert not marker_a.exists(), (
        'The poisoned cache module was EXECUTED (V1): the marker file was '
        'created')
    assert not hasattr(second, 'POISONED'), (
        'The poisoned cache module was returned (V1)')
    assert sorted(second.types) == TINY_TYPES, (
        'the regenerated module must be a proper ASN.1 AST')
    assert second.asn1Files == [asn1_file]
    # The entry is healthy again (the manifest is always written last)
    assert os.path.isfile(cache_manifest(project_cache, key)), (
        'the regeneration did not rewrite the cache manifest')
    with open(cache_py(project_cache, key), 'rb') as source:
        assert b'POISONED' not in source.read(), (
            'the poisoned module is still in the cache after the parse')

    # (b) The manifest is present, but the hash of the module does not
    #     match the one recorded in the manifest
    marker_b = tmp_path / 'poison_executed_case_b.marker'
    plant_module(project_cache, key, marker_b)
    clear_in_memory_caches()

    third = parse_asn1([asn1_file], pretty_print=True)

    assert not marker_b.exists(), (
        'The poisoned cache module was EXECUTED although its manifest was '
        'present (V1)')
    assert not hasattr(third, 'POISONED'), (
        'The poisoned cache module was returned although its manifest was '
        'present (V1)')
    assert 'Not reusing the ASN.1 cache entry' in caplog.text, (
        'the rejection of the poisoned entry must be visible in the log')


@pytest.mark.skipif(os.name != 'posix',
                    reason='POSIX-only: file permission checks')
def test_cache_poisoning_rejected_world_writable(project_cache, tmp_path):
    ''' V1 (POSIX): a cache artifact that is group- or world-writable is
        not trusted (another user of the machine could have replaced it):
        the entry is regenerated, the payload does not run. On the
        vulnerable code the artifact was used regardless of its
        permissions. '''
    asn1_file = unique_tiny_asn1(tmp_path, 'world_writable')
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__
    marker = tmp_path / 'poison_executed_world_writable.marker'

    plant_module(project_cache, key, marker)
    os.chmod(cache_py(project_cache, key), 0o666)
    clear_in_memory_caches()

    second = parse_asn1([asn1_file], pretty_print=True)

    assert not marker.exists(), (
        'A world-writable poisoned cache module was EXECUTED (V1)')
    assert not hasattr(second, 'POISONED'), (
        'A world-writable poisoned cache module was returned (V1)')


@pytest.mark.skipif(os.name != 'posix', reason='POSIX-only: symlinks')
def test_cache_poisoning_rejected_symlink(project_cache, tmp_path):
    ''' V1 (POSIX): a cache artifact replaced by a symbolic link is not
        trusted: the entry is regenerated, the payload does not run. '''
    asn1_file = unique_tiny_asn1(tmp_path, 'symlink')
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__
    marker = tmp_path / 'poison_executed_symlink.marker'

    # The payload module outside of the cache, the cache entry replaced
    # by a link to it
    payload = tmp_path / 'payload.module.py'
    payload.write_text(make_poison_payload(marker))
    os.remove(cache_py(project_cache, key))
    os.symlink(str(payload), cache_py(project_cache, key))
    sys.modules.pop(key, None)
    clear_in_memory_caches()

    second = parse_asn1([asn1_file], pretty_print=True)

    assert not marker.exists(), (
        'A cache module replaced by a symbolic link was EXECUTED (V1)')
    assert not hasattr(second, 'POISONED'), (
        'A cache module replaced by a symbolic link was returned (V1)')


@pytest.mark.skipif(os.name != 'posix', reason='POSIX-only: file modes')
def test_generation_writes_through_own_file(project_cache, tmp_path):
    ''' V1 (remediation): a stale artifact planted in the cache folder (here
        group/world-writable, as another user of a shared cache folder
        could leave it) is not written through: it is removed before the
        compiler runs, and a new file owned by the current user is created
        instead. The test holds an open file descriptor on the planted
        file: an unlinked file keeps its descriptor (its content stays
        readable, and its link count drops to zero), while a file that was
        written through keeps its link count and has its content replaced -
        so the two cases cannot be confused, not even by an inode number
        that the kernel may reuse after the unlink.
        On the pre-remediation code the compiler wrote through the planted
        file, so its owner and its 0666 mode survived the generation. '''
    asn1_file = unique_tiny_asn1(tmp_path, 'wrote_through')
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__

    # Replace the module with a planted, group/world-writable file
    planted = cache_py(project_cache, key)
    os.remove(planted)
    with open(planted, 'w', encoding='utf-8') as source:
        source.write('POISONED = True\n')
    os.chmod(planted, 0o666)
    planted_fd = os.open(planted, os.O_RDONLY)
    clear_in_memory_caches()
    try:
        second = parse_asn1([asn1_file], pretty_print=True)

        assert not hasattr(second, 'POISONED'), (
            'the content of the planted file survived the regeneration (V1)')
        assert sorted(second.types) == TINY_TYPES
        # The planted file was removed (unlinked), not written through
        assert os.fstat(planted_fd).st_nlink == 0, (
            'the ASN.1 compiler wrote through the planted cache file: a '
            'file that another user left in a shared cache folder was '
            'never removed (V1 remediation)')
        os.lseek(planted_fd, 0, os.SEEK_SET)
        assert b'POISONED' in os.read(planted_fd, 4096), (
            'the planted file was overwritten: the compiler wrote through '
            'it (V1 remediation)')
        # The artifact that is on the disk now is a new file, with
        # restrictive permissions
        mode = stat.S_IMODE(os.stat(planted).st_mode)
        assert mode & 0o022 == 0, (
            'the regenerated cache file is group- or world-writable '
            '(V1/V8 remediation)')
    finally:
        os.close(planted_fd)


@pytest.mark.skipif(os.name != 'posix', reason='POSIX-only: file modes')
def test_generation_rejects_replaced_artifact(project_cache, tmp_path,
                                              monkeypatch):
    ''' V1 (remediation): if the artifact is REPLACED by another file while
        the ASN.1 compiler runs (a new inode - the file that this process
        created before the generation is removed and a payload is put in
        its place), the bytes that are read back are not the bytes that
        were created here, and they are not executed.
        The ownership check is what rejects the replacement in the threat
        model of the audit (an attacker is another USER of the machine).
        The file cannot really be chowned to another user without root
        privileges, so the test simulates it: os.getuid returns the uid of
        "another user" while the file is checked - the replaced file has a
        new inode, so it is the ownership check that must catch it.
        On the pre-remediation code the freshly read bytes were executed
        without any check at all. '''
    asn1_file = unique_tiny_asn1(tmp_path, 'replaced_artifact')
    marker = tmp_path / 'poison_executed_replaced.marker'
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__
    target = cache_py(project_cache, key)

    # Force a regeneration of this entry (otherwise the warm cache is
    # simply reused and the compiler is not invoked at all)
    os.remove(cache_manifest(project_cache, key))

    real_waitfor = Asn1scc.waitfor_qprocess
    real_getuid = os.getuid
    replaced = []

    def replace_artifact(qprocess, name):
        ''' The "attacker": replace the artifact with a payload right after
            the compiler finished, before opengeode reads it back. From this
            point on, the file is "owned by another user" (the flag makes
            os.getuid report the uid of someone else, because a real chown
            to another user needs root privileges) '''
        result = real_waitfor(qprocess, name)
        if name == 'ASN.1 Compiler':
            os.remove(target)
            with open(target, 'w', encoding='utf-8') as payload:
                payload.write(make_poison_payload(marker))
            replaced.append(True)
        return result

    def getuid_of_the_attacker():
        ''' Between the replacement and the rejection, the process "is" the
            other user for every ownership check '''
        if replaced:
            return real_getuid() + 1
        return real_getuid()

    monkeypatch.setattr(Asn1scc, 'waitfor_qprocess', replace_artifact)
    monkeypatch.setattr(os, 'getuid', getuid_of_the_attacker)
    clear_in_memory_caches()

    with pytest.raises(TypeError, match='cannot be trusted'):
        parse_asn1([asn1_file], pretty_print=True)
    assert not marker.exists(), (
        'An artifact replaced during the generation by another user was '
        'EXECUTED (V1 remediation): the bytes read after the compiler ran '
        'were not the bytes that were created before it')
    # The cache was left without a manifest: the next run regenerates
    assert not os.path.isfile(cache_manifest(project_cache, key))


def test_generation_failsafe_unremovable_entry(project_cache, tmp_path):
    ''' V1/F2 (remediation): when a cache file cannot be removed before the
        generation (e.g. it belongs to another user in a folder with the
        sticky bit, or the folder is read-only), opengeode refuses to write
        through it instead of executing whatever may end up in it. The
        failure is a TypeError, like every other failure of the ASN.1
        chain.
        The miss is provoked by removing the manifest (an interrupted
        generation): the entry must be regenerated, and the regeneration
        must fail clearly rather than write through files it does not
        control. '''
    asn1_file = unique_tiny_asn1(tmp_path, 'unremovable')
    first = parse_asn1([asn1_file], pretty_print=True)
    key = first.__name__

    # Force a cache miss, and make the folder read-only: the removal of
    # the stale artifacts must fail
    os.remove(cache_manifest(project_cache, key))
    os.chmod(project_cache, 0o555)
    clear_in_memory_caches()
    try:
        with pytest.raises(TypeError, match='cannot be replaced'):
            parse_asn1([asn1_file], pretty_print=True)
    finally:
        os.chmod(project_cache, 0o755)

    # Nothing was written through the stale entry, and no manifest was
    # written: the next run (with the folder writable again) regenerates
    assert not os.path.isfile(cache_manifest(project_cache, key))
    clear_in_memory_caches()
    second = parse_asn1([asn1_file], pretty_print=True)
    assert sorted(second.types) == TINY_TYPES
    assert second.asn1Files == [asn1_file]


@pytest.mark.skipif(os.name != 'posix', reason='POSIX-only: file modes')
def test_debug_cache_poisoning_rejected(project_cache, tmp_path, caplog,
                                        monkeypatch):
    ''' V4: in debug mode ("-g" on the command line) the ASN.1 modules are
        cached in "./debug" instead of $PROJECT_CACHE: a payload planted
        there must be rejected exactly like in any other cache folder
        (same code path, but it must be proven: the directory is the current
        one, whose permissions are those of the project). '''
    caplog.set_level(logging.INFO, logger='opengeode.Asn1scc')
    workdir = tmp_path / 'debug_project'
    workdir.mkdir()
    asn1_file = workdir / 'dataview.asn'
    asn1_file.write_text(TINY_ASN1.replace(
        '\nEND\n', '\n-- Unique content of test "debug_poisoning"\n\nEND\n'))
    marker = tmp_path / 'poison_executed_debug.marker'

    monkeypatch.setattr(sys, 'argv', ['opengeode', '-g'])  # ./debug cache
    monkeypatch.chdir(workdir)                # "./debug" is relative to cwd
    try:
        debug_cache = str(workdir / 'debug')
        first = parse_asn1([str(asn1_file)], pretty_print=True)
        key = first.__name__
        assert os.path.realpath(os.path.dirname(
            cache_py(debug_cache, key))) == os.path.realpath(debug_cache)

        # Poison the entry, and parse again
        plant_module(debug_cache, key, marker)
        clear_in_memory_caches()
        second = parse_asn1([str(asn1_file)], pretty_print=True)

        assert not marker.exists(), (
            'A poisoned module of the ./debug cache was EXECUTED (V4)')
        assert not hasattr(second, 'POISONED'), (
            'A poisoned module of the ./debug cache was returned (V4)')
        assert sorted(second.types) == TINY_TYPES
        # The debug cache folder is created with restrictive permissions
        mode = stat.S_IMODE(os.stat(debug_cache).st_mode)
        assert mode & 0o077 == 0, (
            'the debug cache folder must not be accessible by group or '
            'other users, found ' + oct(mode) + ' (V8)')
    finally:
        sys.argv = ['opengeode']


def test_old_md5_entry_ignored(project_cache, tmp_path):
    ''' V1 support: an old-format cache entry - the 32-hex (md5) module
        files written by the previous version of the cache, without any
        manifest - is never loaded: the parse regenerates the module under
        its new sha256 name. The old entry stays on the disk, harmless.
        (A shared cache folder of a TASTE installation can legitimately
        contain such entries.) '''
    asn1_file = unique_tiny_asn1(tmp_path, 'old_md5_entry')
    # The key used by the vulnerable code: md5 of the content of the file
    with open(asn1_file, 'rb') as source:
        old_key = hashlib.md5(source.read()).hexdigest()
    marker = tmp_path / 'poison_executed_old_entry.marker'
    # Plant an old-format entry: a payload module and a html file (so that
    # the vulnerable code, which required both to exist, would reuse it)
    os.makedirs(project_cache, exist_ok=True)
    plant_module(project_cache, old_key, marker)
    with open(cache_html(project_cache, old_key), 'w',
              encoding='utf-8') as html:
        html.write('<html><body>old cache entry</body></html>')
    clear_in_memory_caches()

    ast = parse_asn1([asn1_file], pretty_print=True)

    assert not marker.exists(), (
        'An old-format (manifest-less) cache module was EXECUTED (V1)')
    assert not hasattr(ast, 'POISONED'), (
        'An old-format (manifest-less) cache module was loaded (V1)')
    assert sorted(ast.types) == TINY_TYPES
    # The old entry is simply ignored: a new, sha256-named entry was
    # created next to it, and the old files were left untouched
    assert os.path.isfile(cache_py(project_cache, ast.__name__))
    assert os.path.isfile(cache_py(project_cache, old_key)), (
        'the old-format entry must be left on the disk (harmless), not '
        'deleted')


def test_manifest_written(project_cache, tiny_asn1_file):
    ''' V1 support: after a cold parse, a ".manifest" JSON file exists
        next to the generated module. It parses, and it records the
        options of the parse, a fingerprint of the ASN.1 compiler, the
        content hash of the input files and the sha256 of the generated
        artifacts - matching the actual files. On the vulnerable code
        there was no manifest at all: nothing tied a cached module to the
        inputs it was generated from. '''
    parse_asn1([tiny_asn1_file],
               rename_policy=ASN1.SystematicRenameAllEnumerants,
               pretty_print=True)

    manifests = manifest_files(project_cache)
    assert len(manifests) == 1, (
        f'expected exactly one cache manifest, found {manifests}')
    manifest_path = manifests[0]

    with open(manifest_path, encoding='utf-8') as source:
        manifest = json.load(source)

    assert isinstance(manifest, dict)
    # The options of the parse, stored as plain (JSON-serializable) values
    assert manifest['key_options'] == {
            'ast_version': ASN1.UniqueEnumeratedNames.value,
            'rename_policy': ASN1.SystematicRenameAllEnumerants.value,
            'flags': sorted(flag.value for flag in [ASN1.AstOnly]),
            'extraflags': [],
            'pretty_print': True}, (
        f'the manifest must record the effective options of the parse, '
        f'found {manifest["key_options"]}')
    # A fingerprint of the compiler (a new asn1scc version must not reuse
    # an entry generated by the previous one)
    assert os.path.isfile(manifest['tool']['path']), (
        'the manifest must record the path of the ASN.1 compiler')
    # The hash of each input file
    assert manifest['inputs'] == [[tiny_asn1_file,
                                   sha256_of(tiny_asn1_file)]], (
        f'the manifest must record the sha256 of each input, found '
        f'{manifest["inputs"]}')
    # The hashes of the artifacts, matching the actual files
    key = os.path.basename(manifest_path)[:-len('.manifest')]
    assert manifest['artifacts']['py'] == sha256_of(
        cache_py(project_cache, key)), (
        'the manifest hash of the generated module does not match the file')
    assert manifest['artifacts']['html'] == sha256_of(
        cache_html(project_cache, key)), (
        'the manifest hash of the generated HTML file does not match the '
        'file')


def test_html_tampering_detected(project_cache, tiny_asn1_file, caplog):
    ''' V9: a tampered (e.g. replaced) cached HTML file is not returned to
        the GUI: its hash no longer matches the manifest, so the entry is
        regenerated. On the vulnerable code the html file was returned as
        it was, without any check. '''
    caplog.set_level(logging.INFO, logger='opengeode.Asn1scc')
    first = parse_asn1([tiny_asn1_file], pretty_print=True)
    key = first.__name__
    assert 'DOCTYPE' in first.html

    with open(cache_html(project_cache, key), 'w', encoding='utf-8') as fl:
        fl.write('<html><body>TAMPERED HTML</body></html>')
    clear_in_memory_caches()

    second = parse_asn1([tiny_asn1_file], pretty_print=True)
    assert 'TAMPERED HTML' not in second.html, (
        'A tampered cached HTML file was returned (V9)')
    assert 'Not reusing the ASN.1 cache entry' in caplog.text


# -----------------------------------------------------------------------------
# V2 - a module planted in the working directory does not shadow the
#      generated module
# -----------------------------------------------------------------------------

def test_cwd_shadowing_rejected(tmp_path, no_project_cache, monkeypatch):
    ''' V2: without any cache folder, a payload module named after the
        cache key planted in the current directory must not be imported:
        the returned module is the one generated by the ASN.1 compiler.
        On the vulnerable code the generated module was imported BY NAME
        after sys.path.append(outdir) - the current directory was searched
        first, so the planted module won and was executed.
        The module directory is put at the front of sys.path here because
        that is the precondition of the attack (Python started from the
        project directory, e.g. with an empty PYTHONPATH entry); the fix
        must be immune to it, since the import must not use sys.path. '''
    # The "project directory of the attacker": it contains the model, its
    # ASN.1 file, and the planted payload module. The content is unique to
    # this test so that the planted module cannot be hidden by the file of
    # another test (see unique_tiny_asn1).
    model_dir = tmp_path / 'attacker_project'
    model_dir.mkdir()
    asn_file = model_dir / 'dataview.asn'
    asn_file.write_text(TINY_ASN1.replace(
        '\nEND\n', '\n-- Unique content of test "cwd_shadowing"\n\nEND\n'))
    marker = model_dir / 'poison_executed_cwd.marker'

    # First call: learn the key of this content with these options
    first = parse_asn1([str(asn_file)], rename_policy=ASN1.NoRename)
    key = first.__name__

    # The attacker plants the payload module named after the key
    plant_module(str(model_dir), key, marker)
    assert (model_dir / (key + '.py')).is_file()

    # Open the model from the attacker's directory
    monkeypatch.syspath_prepend(str(model_dir))
    monkeypatch.chdir(model_dir)
    syspath_snapshot = list(sys.path)
    clear_in_memory_caches()

    second = parse_asn1([str(asn_file)], rename_policy=ASN1.NoRename)

    assert not marker.exists(), (
        'The payload module planted in the current directory was EXECUTED '
        '(V2): the generated module is not imported by path')
    assert not hasattr(second, 'POISONED'), (
        'The payload module planted in the current directory was returned '
        '(V2)')
    assert second.__name__ == key
    assert second is not first
    assert sorted(second.types) == TINY_TYPES, (
        'the returned module must be the one generated by the ASN.1 '
        'compiler, not the planted file')
    assert second.asn1Files == [str(asn_file)]
    # parse_asn1 must not use sys.path at all (the vulnerable code was
    # appending its output folder to it at every call)
    assert sys.path == syspath_snapshot, (
        'parse_asn1 modified sys.path (V2): the import must not go '
        'through sys.path')


# -----------------------------------------------------------------------------
# V5 - validation of the input files
# -----------------------------------------------------------------------------

def test_dash_filename_rejected(tmp_path, monkeypatch, qprocess_bomb):
    ''' V5: an ASN.1 file whose NAME starts with "-" (here "-typePrefix",
        a real option of asn1scc) is an argument-injection attempt: it must
        be rejected with a TypeError BEFORE any external tool is started
        (QProcess.start is booby-trapped here). On the vulnerable code the
        name was appended unchecked to the asn1scc arguments and was
        parsed as an option. '''
    monkeypatch.chdir(tmp_path)
    (tmp_path / '-typePrefix').write_text(TINY_ASN1)
    with pytest.raises(TypeError, match='must not start with "-"'):
        parse_asn1(['-typePrefix'])
    # The file that existed next to it was not touched
    assert (tmp_path / '-typePrefix').is_file()


def test_dash_filename_rejected_asn2dataModel(tmp_path, monkeypatch,
                                              qprocess_bomb):
    ''' V5: asn2dataModel also rejects a file name starting with "-",
        before starting any external tool (cat, asn2dataModel, make) '''
    monkeypatch.chdir(tmp_path)
    (tmp_path / '-typePrefix').write_text(TINY_ASN1)
    with pytest.raises(TypeError, match='must not start with "-"'):
        asn2dataModel(['-typePrefix'])


def test_missing_file_rejected(qprocess_bomb):
    ''' V5-adjacent contract: a file that does not exist is rejected with
        a TypeError, before any external tool is started. (This also
        guards the TypeError convention of the callers, e.g.
        ogParser.set_global_DV, which reports "ASN.1 compiler failed".
        On the vulnerable code, asn2dataModel raised a raw
        FileNotFoundError from os.path.getmtime, breaking that convention,
        and parse_asn1 discovered the missing file only while hashing
        it.) '''
    missing = os.path.join(os.getcwd(), 'no_such_asn1_file_of_mine.asn')
    assert not os.path.exists(missing)
    with pytest.raises(TypeError, match='not found'):
        parse_asn1([missing])
    with pytest.raises(TypeError, match='not found'):
        asn2dataModel([missing])


# -----------------------------------------------------------------------------
# V7 - asn2dataModel: sys.path always restored, new inputs -> new dataview
# -----------------------------------------------------------------------------

def test_syspath_restored_after_asn2dataModel():
    ''' V7: asn2dataModel must leave sys.path exactly as it found it, and
        two calls with different input sets must return the dataview of
        the CURRENT inputs: a new module object with the types of both
        files, without mutating the dataview of the first call.
        On the vulnerable code the modules had a fixed name and the cache
        was keyed by that name: the second call returned the module OBJECT
        of the first call (importlib.reload re-executed the new code into
        it), so the first caller saw its dataview mutate under its feet. '''
    syspath_snapshot = list(sys.path)

    module_one = asn2dataModel([DV1])
    assert sys.path == syspath_snapshot, (
        'sys.path was not restored after asn2dataModel (V7)')
    assert hasattr(module_one, 'MyData'), 'dv1.asn defines MyData'
    assert not hasattr(module_one, 'Ahah'), (
        'the dataview of dv1.asn alone must not contain the types of '
        'dv2.asn')

    module_two = asn2dataModel([DV1, DV2])
    assert sys.path == syspath_snapshot, (
        'sys.path was not restored after the second asn2dataModel call '
        '(V7)')

    assert module_two is not module_one, (
        'asn2dataModel returned the module of the FIRST call to the '
        'second call with different input files (V7: stale dataview)')
    assert hasattr(module_two, 'MyData'), 'the second call keeps dv1.asn'
    assert hasattr(module_two, 'Ahah'), (
        'the second call must return the dataview of dv1+dv2 (Ahah is '
        'defined in dv2.asn), not the dataview of the first call (V7)')
    assert getattr(module_two, 'asn1Files', None) == [DV1, DV2]
    # And the dataview of the first call was not mutated by the second one
    assert not hasattr(module_one, 'Ahah'), (
        'the second call mutated the dataview of the first call (V7)')


def test_asn2dataModel_failure_restores_syspath(tmp_path):
    ''' V7: sys.path is restored even when one of the external tools of
        asn2dataModel fails (the try/finally of the fix). The failure is
        provoked with an ASN.1 file that the DMT tools cannot process.
        On the vulnerable code sys.path.pop(0) was not in a finally block:
        the temporary output folder stayed at the FRONT of sys.path for
        the rest of the process, so any later "import" in the process
        could pick a file from it. '''
    broken = tmp_path / 'broken.asn'
    broken.write_text('Broken-DV DEFINITIONS ::= BEGIN\n'
                      '  My-Seq ::= SEQUEN')
    syspath_snapshot = list(sys.path)
    with pytest.raises(TypeError):
        asn2dataModel([str(broken)])
    assert sys.path == syspath_snapshot, (
        'sys.path was not restored after a FAILED asn2dataModel call '
        '(V7): the temporary output folder leaked at the front of '
        'sys.path')


# -----------------------------------------------------------------------------
# Performance guards: a cache hit must still skip the compiler
# -----------------------------------------------------------------------------

def test_in_memory_cache_reuse(tiny_asn1_file, monkeypatch, caplog):
    ''' No regression: two identical calls (same files, same options) hit
        the in-memory AST cache: the same module object is returned, and
        the second call does not invoke the ASN.1 compiler (any lookup of
        the asn1scc binary after the first call fails the test). '''
    caplog.set_level(logging.INFO, logger='opengeode.Asn1scc')
    first = parse_asn1([tiny_asn1_file])
    arm_asn1scc_lookup(monkeypatch)     # armed only for the second call
    second = parse_asn1([tiny_asn1_file])
    assert second is first, (
        'two identical parse_asn1 calls must return the same module '
        'object (in-memory AST reuse - a performance guarantee)')
    assert 'Reusing ASN.1 model from cache' in caplog.text


def test_warm_cache_skips_compiler(project_cache, tiny_asn1_file,
                                   monkeypatch, caplog):
    ''' No regression: with a warm on-disk cache and a fresh in-memory AST
        dict (the situation of a second process, or of a model reloaded
        after a change of options), the parse must complete WITHOUT
        calling the ASN.1 compiler (any start of an external tool fails
        the test; the lookup of the compiler is legitimate here, because
        the manifest check fingerprints it). This guards the performance
        of the cache: only input hashing and one hash check are added on
        the warm path. '''
    caplog.set_level(logging.INFO, logger='opengeode.Asn1scc')
    first = parse_asn1([tiny_asn1_file], pretty_print=True)
    assert os.path.isfile(cache_py(project_cache, first.__name__))

    Asn1scc.AST.clear()                  # fresh in-memory cache
    arm_qprocess(monkeypatch,
                 'The ASN.1 compiler was invoked although the warm cache '
                 'entry should have been reused')
    second = parse_asn1([tiny_asn1_file], pretty_print=True)

    assert second.__name__ == first.__name__
    assert sorted(second.types) == TINY_TYPES
    assert 'Reusing cached ASN.1 modules from' in caplog.text, (
        'the warm cache entry was not reused: the fix would cost the '
        'performance of the tool (the ASN.1 compiler must be skipped '
        'when the cache is warm)')


# -----------------------------------------------------------------------------
# V8 - permissions of the cache folder
# -----------------------------------------------------------------------------

@pytest.mark.skipif(os.name != 'posix', reason='POSIX-only permission checks')
def test_cache_dir_created_0700(project_cache, tiny_asn1_file):
    ''' V8: a cache folder that does not exist yet is created with mode
        0o700 (only the owner can use it), and not with the permissive
        default mode of os.makedirs. The umask is forced to 0 during the
        parse, so that the exact 0o700 can be asserted and so that the
        test also checks that the artifacts written in the cache are
        hardened: the fix must strip the group/world write bits itself,
        whatever the umask of the user is.
        On the vulnerable code the folder was created 0o777&~umask and the
        files 0o666&~umask: with a permissive umask, any user of the
        machine could write in the cache. '''
    current_umask = os.umask(0o000)
    try:
        parse_asn1([tiny_asn1_file])
    finally:
        os.umask(current_umask)

    mode = stat.S_IMODE(os.stat(project_cache).st_mode)
    assert mode == 0o700, (
        'the cache folder must be created with mode 0o700, found '
        + oct(mode) + ' (V8)')
    artifacts = py_files(project_cache) + manifest_files(project_cache)
    for path in artifacts:
        artifact_mode = stat.S_IMODE(os.stat(path).st_mode)
        assert artifact_mode & 0o022 == 0, (
            f'the cache artifact {path} is group- or world-writable ('
            + oct(artifact_mode) + ') - another user of the machine could '
            'replace it (V8)')


# -----------------------------------------------------------------------------
# No regression: shape of the returned AST
# -----------------------------------------------------------------------------

def test_returned_ast_attributes(tiny_asn1_file):
    ''' Contract: the fixed parse must still return a module with the
        attributes that the rest of opengeode relies on: asn1Files (the
        files of THIS project, also on a cache hit), html (the generated
        pretty-printed HTML, or an empty string), and the types of the
        ASN.1 data view.
        On the vulnerable code this fails too: pretty_print was not part
        of the cache key (V3), so the plain parse returned the module of
        the pretty-printed one, with its stale "html" attribute. '''
    ast = parse_asn1([tiny_asn1_file], pretty_print=True)
    assert sorted(ast.types) == TINY_TYPES
    assert ast.asn1Files == [tiny_asn1_file]
    assert 'DOCTYPE' in ast.html, (
        'pretty_print=True must set ast.html to the generated HTML file')
    assert '<html' in ast.html.lower() or '<body' in ast.html.lower()

    plain = parse_asn1([tiny_asn1_file])
    assert plain.asn1Files == [tiny_asn1_file]
    assert plain.html == '', 'without pretty_print, ast.html must be ""'
