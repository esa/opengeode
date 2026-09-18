#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Python API for the ASN1Scc compiler

    Copyright (c) 2013-2024 European Space Agency

    Designed and implemented by Maxime Perrotin

    Based on the ASN.1 Space Certified Compiler (ASN1SCC)

    Contact: maxime.perrotin@esa.int
"""

import atexit
import hashlib
import importlib.util
import json
import logging
import os
import distutils.spawn as spawn
import shutil
import stat
import sys
import tempfile
from PySide6.QtCore import QProcess, QFile, QIODevice

LOG = logging.getLogger(__name__)
terminal_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
handler_console = logging.StreamHandler()
handler_console.setFormatter(terminal_formatter)
LOG.addHandler(handler_console)

# global needed to store the imported module and list of modules ever loaded
AST = {}

# Same for the modules imported by the call to asn2dataModel
ASN2DM = {}

# Temporary folders created by asn2dataModel, removed when the process ends
# (they are kept during the whole process because the modules that were
# generated in them can still be used after the call returned)
_ASN2DM_TEMP_DIRS = set()

# Set once a shared-writable cache folder has been reported to the user
_SHARED_CACHE_WARNED = False

# Name of the concatenated ASN.1 file created by asn2dataModel, and of the
# modules that it generates, in import dependency order (DV_Types is
# imported by Stubs, og_dataview_asn imports DV and Stubs, db_model imports
# og_dataview_asn and DV)
_DMT_PREFIX = 'og_dataview'
_DMT_MODULES = ('DV_Types', 'Stubs', 'DV', _DMT_PREFIX + '_asn', 'db_model')

try:
    from enum import Enum
except ImportError:
    raise ImportError('Enum module not found. Run pip install --user enum34')


__all__ = ['ASN1', 'parse_asn1', 'create_choice_determinant_types']


class ASN1(Enum):
    ''' Flags used to control the compiler options '''
    NoParameterizedTypes = 1
    NoInnerTypes = 2
    NoConstraintReference = 3
    UniqueEnumeratedNames = 4
    AstOnly = 5
    NoRename = 0
    RenameOnlyConflicting = 1 # C default
    RenameAllEnumerants = 2   # All if at least one conflict
    SystematicRenameAllEnumerants = 3 # All no matter what

def waitfor_qprocess(qprocess, name):
    ''' Wait the execution of a QProcess instance
    Raise an exception if anything went wrong, otherwise return stdout '''
    if not qprocess.waitForStarted():
        raise TypeError('Could not start ' + name)
    if not qprocess.waitForFinished(300000):
        raise TypeError('Execution time out : ' + name)
    exitcode = qprocess.exitCode()
    err = qprocess.readAllStandardError()
    std = qprocess.readAllStandardOutput()
    if exitcode != 0:
        raise TypeError(f'{name} error (exit code = {exitcode}) - {str(err)}')
    return std


def _validate_input_files(file_list):
    ''' Check the ASN.1 files before they are passed to the external tools.
        File names coming from a model (USE clause / CIF annotations) must
        not be parsed as options by asn1scc, and must exist. '''
    for each in file_list:
        if each.startswith('-'):
            raise TypeError('Invalid ASN.1 file name "{}": file names must '
                            'not start with "-" (they are passed as options '
                            'to the ASN.1 tools)'.format(each))
        if not os.path.isfile(each):
            raise TypeError(f'ASN.1 file not found: {each}')


def _read_input_files(file_list):
    ''' Read each input file once, in binary mode
        Return a list of (file name, content) tuples '''
    contents = []
    for each in file_list:
        try:
            with open(each, 'rb') as asn1_file:
                contents.append((each, asn1_file.read()))
        except OSError as err:
            raise TypeError(str(err))
    return contents


def _effective_options(ast_version, rename_policy, flags, extraflags,
                       pprint):
    ''' Return the effective compiler options as a plain, JSON-serializable
        object. These options change the generated AST, so they are part of
        the cache key and are stored in the cache manifest. '''
    return {'ast_version': getattr(ast_version, 'value', ast_version),
            'rename_policy': getattr(rename_policy, 'value', rename_policy),
            'flags': sorted(getattr(each, 'value', each) for each in flags),
            'extraflags': list(extraflags),
            'pretty_print': bool(pprint)}


def _tool_fingerprint(binary):
    ''' Fingerprint of the ASN.1 compiler: a cache entry that was generated
        with another version of the compiler is never reused '''
    try:
        stats = os.stat(binary)
    except OSError as err:
        raise TypeError(f'Could not check the ASN.1 compiler: {err}')
    return {'path': os.path.abspath(binary),
            'size': stats.st_size,
            'mtime': stats.st_mtime}


def _harden_cache_file_perms(filepaths):
    ''' Make sure the files that were just been written in the cache folder
        are not group/world-writable, whatever the umask of the user. This
        is only done on the files created by this run - an existing shared
        cache folder is never modified. '''
    if os.name != 'posix':
        return
    for each in filepaths:
        try:
            mode = stat.S_IMODE(os.lstat(each).st_mode)
            if mode & 0o022:
                os.chmod(each, mode & ~0o022)
        except OSError:
            # Not fatal: the file will be checked again on the next run
            LOG.info(f'Could not restrict the permissions of {each}')


def _warn_if_shared_writable(cache_dir):
    ''' Warn the user (once) if the cache folder can be written by other
        users. The cached files are individually checked before use, so
        this is only a warning: shared cache folders must keep working. '''
    global _SHARED_CACHE_WARNED
    if os.name != 'posix' or _SHARED_CACHE_WARNED:
        return
    try:
        mode = stat.S_IMODE(os.stat(cache_dir).st_mode)
    except OSError:
        return
    if mode & 0o022:
        LOG.warning(f'The ASN.1 cache folder "{cache_dir}" is group- or '
                    'world-writable: other users of this machine can '
                    'tamper with it. These entries are checked before use, '
                    'but consider restricting its permissions.')
        _SHARED_CACHE_WARNED = True


def _verify_cached_artifact(filepath, check_mode=True):
    ''' Read one file of a cache entry, after having checked that it is not
        a symbolic link and, on POSIX systems, that it belongs to the
        current user and (unless check_mode is False) is not group- or
        world-writable. The file is checked and read through one and the
        same open file descriptor: no file replaced between the check and
        the read can slip through.
        check_mode is False for a file that was just generated (outside a
        cache folder, or one of the modules generated by asn2dataModel):
        its permissions simply follow the umask of the user (the folder
        that contains it is private), so only the link and ownership are
        checked.
        Return (content, None) or (None, reason) - never raise '''
    if os.path.islink(filepath):
        return None, f'"{filepath}" is a symbolic link'
    try:
        with open(filepath, 'rb') as artifact:
            if os.name == 'posix':
                stats = os.fstat(artifact.fileno())
                if stats.st_uid != os.getuid():
                    return None, (f'"{filepath}" does not belong to the '
                                  'current user')
                if check_mode and stat.S_IMODE(stats.st_mode) & 0o022:
                    return None, f'"{filepath}" is group- or world-writable'
            content = artifact.read()
    except OSError as err:
        return None, f'"{filepath}": {err}'
    return content, None


def _remove_stale_cache_entry(paths):
    ''' Remove the files of a cache entry that is about to be generated
        again. They may belong to another user of a shared cache folder:
        writing through them would let that user choose the content that is
        executed, and a manifest that stays behind would vouch for files
        that were replaced. A file that cannot be removed (e.g. in a folder
        with the sticky bit) means the folder cannot be used as a cache:
        fail clearly instead. '''
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as err:
            raise TypeError(f'The ASN.1 cache file "{path}" cannot be '
                            f'replaced (it may belong to another user of a '
                            f'shared cache folder): {err}')


def _read_generated_artifact(filepath, fd):
    ''' Read one file that the ASN.1 compiler has just generated.
        In a cache folder, "fd" is the descriptor of the very file that
        this process created before the generation (see
        _precreate_cache_artifacts): the content is read from it, after
        checking that the file behind it still belongs to the current user.
        The bytes read are the bytes that the compiler wrote through that
        descriptor: no replacement of the file at its path can influence
        them. "fd" is None outside a cache folder (and on Windows): the
        file is then read by path, after the usual link/ownership checks.
        Return (content, None) or (None, reason) - never raise '''
    if fd is None:
        return _verify_cached_artifact(filepath, check_mode=False)
    try:
        if os.name == 'posix' and os.fstat(fd).st_uid != os.getuid():
            return None, (f'"{filepath}" does not belong to the '
                          'current user')
        # Read the whole file from the descriptor: its offset was never
        # moved (the compiler wrote through its own descriptor), so this
        # reads the content from its very beginning
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
        return b''.join(chunks), None
    except OSError as err:
        return None, f'"{filepath}": {err}'


def _precreate_cache_artifacts(paths):
    ''' Create the artifact files of a cache entry before the ASN.1 compiler
        is started, owned by the current user and writable by nobody else:
        the compiler writes through them (it truncates, it does not replace
        them), so no other user of a shared cache folder can make the file
        group-writable and tamper with it during the generation.
        The file descriptors are returned OPEN: the caller reads the
        generated content from these very descriptors after the generation
        (they are truncated and rewritten through them by the compiler), so
        that no replacement of the file at its path - not even one with the
        very same inode number, which the kernel may reuse after an unlink -
        can make this code execute anything else than what the compiler
        wrote. The caller closes the descriptors.
        On Windows the files are not created here: the behavior of the
        compiler is left exactly as it was. '''
    descriptors = {}
    if os.name != 'posix':
        return descriptors
    for path in paths:
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            # Already removed by _remove_stale_cache_entry; if it appeared
            # again in between, fail rather than write through a stranger
            raise TypeError(f'The ASN.1 cache file "{path}" cannot be '
                            'created (it already exists)')
        except OSError as err:
            raise TypeError(f'The ASN.1 cache file "{path}" cannot be '
                            f'created: {err}')
        descriptors[path] = fd
    return descriptors


def _check_cache(manifest_path, py_path, html_path, tool, input_hashes,
                 key_options):
    ''' Decide whether the cached ASN.1 modules can be reused.
        Return (None, python content, html content) if the cache entry can
        be trusted, or (reason, None, None) if the ASN.1 compiler must be
        called again. A reason is logged by the caller. Never raise. '''
    manifest_content, reason = _verify_cached_artifact(manifest_path)
    if reason is not None:
        return reason, None, None
    py_content, reason = _verify_cached_artifact(py_path)
    if reason is not None:
        return reason, None, None
    html_content = None
    if html_path is not None:
        html_content, reason = _verify_cached_artifact(html_path)
        if reason is not None:
            return reason, None, None
    try:
        manifest = json.loads(manifest_content.decode('utf-8'))
    except ValueError as err:
        return f'corrupted cache manifest: {err}', None, None
    if not isinstance(manifest, dict):
        return 'corrupted cache manifest', None, None
    if manifest.get('key_options') != key_options:
        return 'cache entry created with different compiler options', None, \
            None
    if manifest.get('tool') != tool:
        return 'cache entry created with another ASN.1 compiler', None, None
    recorded_inputs = manifest.get('inputs')
    if not isinstance(recorded_inputs, list) \
            or len(recorded_inputs) != len(input_hashes):
        return 'cache entry does not match the input files', None, None
    # Only the contents are compared, not the paths: identical ASN.1 files
    # from different projects must share the same cache entry
    for recorded, expected in zip(recorded_inputs, input_hashes):
        if not isinstance(recorded, list) or len(recorded) != 2 \
                or recorded[1] != expected:
            return 'cache entry does not match the input files', None, None
    artifacts = manifest.get('artifacts')
    if not isinstance(artifacts, dict):
        return 'corrupted cache manifest', None, None
    if artifacts.get('py') != hashlib.sha256(py_content).hexdigest():
        return 'cached ASN.1 module does not match its manifest', None, None
    if html_path is not None:
        if artifacts.get('html') != hashlib.sha256(html_content).hexdigest():
            return 'cached HTML file does not match its manifest', None, None
    return None, py_content, html_content


def _write_manifest(manifest_path, manifest):
    ''' Write the manifest of a cache entry. It is always written last, so
        that an interrupted generation leaves no usable entry behind.
        The file was removed before the generation started, so it is created
        here only if it does not exist: anything that appeared in between
        (e.g. in a cache folder writable by another user) is refused rather
        than followed - a symbolic link must not redirect the write. '''
    data = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    _write_file_checked(manifest_path, data, exclusive=True)


def _write_file_checked(filepath, data, exclusive=False):
    ''' Write a file of the cache folder through a file descriptor that
        belongs to the current user, created with restrictive permissions,
        and never through a symbolic link (which could, in a cache folder
        writable by another user, redirect the write to any file).
        With exclusive=True the file must not exist (it was removed by
        _remove_stale_cache_entry): anything that reappeared in between
        is refused. Fail with TypeError, like every other cache error. '''
    flags = (os.O_WRONLY | os.O_CREAT
             | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0))
    flags |= os.O_EXCL if exclusive else os.O_TRUNC
    try:
        fd = os.open(filepath, flags, 0o600)
    except OSError as err:
        raise TypeError(f'Could not write "{filepath}": {err}')
    try:
        if os.name == 'posix' and os.fstat(fd).st_uid != os.getuid():
            raise TypeError(f'Could not write "{filepath}": it belongs to '
                            'another user')
        with os.fdopen(fd, 'wb') as target:
            fd = None     # the file object owns the descriptor from now on
            target.write(data)
    except OSError as err:
        raise TypeError(f'Could not write "{filepath}": {err}')
    finally:
        if fd is not None:
            os.close(fd)


def _import_module_from_source(module_name, filepath, source):
    ''' Import a Python module from a file path, without using sys.path, so
        that no file with the same module name can shadow it (in particular
        from the current folder).
        "source" is the content of the file, already read and checked by the
        caller: it is executed as it is, so that no stale or forged
        __pycache__ bytecode can be used instead of the file that was
        verified. '''
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        raise TypeError(f'Cannot import the generated module "{filepath}"')
    module = importlib.util.module_from_spec(spec)
    # Register the module before executing it, so that the statements of the
    # generated code that import their siblings find this very module
    sys.modules[module_name] = module
    try:
        code = compile(source, filepath, 'exec')
        exec(code, module.__dict__)
    except SyntaxError as err:
        sys.modules.pop(module_name, None)
        raise TypeError(f'The generated module "{filepath}" is not valid '
                        f'Python code: {err}')
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def parse_asn1(*files, **options):
    ''' Call the ASN.1 parser on a number of files, and return the module
        containing the AST
        This function uses QProcess to launch the ASN.1 compiler because
        the subprocess module from Python has issues on the Windows platform

        The result is cached in the folder given by the PROJECT_CACHE
        environment variable (if set). The cache key covers the content of
        the input files and all the compiler options, and a cached module is
        only reused when the manifest written next to it guarantees that it
        is intact, that it belongs to the current user, and that it was
        generated by the same ASN.1 compiler. Otherwise the ASN.1 compiler
        is simply called again.
    '''
    outdir = None
    if '-g' in sys.argv:
        os.environ["PROJECT_CACHE"] = './debug'

    # use basic caching to avoid re-parsing when loading the model
    project_cache = os.getenv("PROJECT_CACHE")
    if project_cache is not None and not os.path.isdir(project_cache):
        try:
            LOG.info(f"Creating cache folder {project_cache}")
            os.makedirs(project_cache, mode=0o700)
        except OSError:
            raise TypeError (f'''The configured cache folder "{project_cache} " \
                is not there and could not be created\n''')

    if project_cache is not None:
        LOG.info(f"ASN.1 Parser: using cache folder {project_cache}")
        _warn_if_shared_writable(project_cache)

    # The effective options are needed to compute the cache key: the same
    # input files parsed with different options give different ASTs
    ast_version = options.get('ast_version', ASN1.UniqueEnumeratedNames)
    rename_policy = options.get('rename_policy', ASN1.NoRename)
    flags = options.get('flags', [ASN1.AstOnly])
    pprint = options.get('pretty_print', False)
    extraflags = options.get('extraflags', [])
    assert isinstance(ast_version, ASN1)
    assert isinstance(rename_policy, ASN1)
    assert isinstance(flags, list)
    key_options = _effective_options(ast_version, rename_policy, flags,
                                     extraflags, pprint)

    # Validate the input files before handing them over to the ASN.1
    # compiler, and read each of them exactly once
    file_list = sorted(list(*files))
    _validate_input_files(file_list)
    inputs = _read_input_files(file_list)

    # names of the files that will be generated by asn1scc and then parsed
    # Depending on command line options (--toC, --toAda, or --toRust), prefix
    # the file name (they use different compilation options)
    if "--toC" in sys.argv:
        prefix = "c_"
    elif "--toRust" in sys.argv:
        prefix = "rust_"
    else:
        prefix = ""

    # Cache key: sha256 of the backend prefix, of the content of each input
    # file (in sorted file name order - the paths are deliberately not
    # hashed, so that identical ASN.1 files from different projects share
    # the same cache entry), of the compiler options, and of the prefix
    # again. The number of input files and the hex digest of each file are
    # hashed instead of their raw content: this self-delimiting encoding
    # makes sure that two different sets of input files can never produce
    # the same key (and reuses the digests computed for the manifest).
    filehash = hashlib.sha256()
    filehash.update(prefix.encode('utf-8'))
    input_hashes = []
    for _, content in inputs:
        input_hashes.append(hashlib.sha256(content).hexdigest())
    filehash.update((str(len(input_hashes)) + ':').encode('utf-8'))
    for digest in input_hashes:
        filehash.update(digest.encode('utf-8'))
    filehash.update(repr(key_options).encode('utf-8'))
    filehash.update(prefix.encode('utf-8'))
    new_hash = prefix + filehash.hexdigest()

    if new_hash in AST.keys():
        LOG.info('Reusing ASN.1 model from cache')
        return AST[new_hash]
    elif project_cache is not None:
        outdir = project_cache
    elif project_cache is None:
        # create a temp folder that will be deleted automatically after use
        tmpoutdir = tempfile.TemporaryDirectory(prefix='OG_ASN1SCC_')
        outdir = tmpoutdir.name

    out_py_name = new_hash + ".py"
    out_html_name = new_hash + ".html"
    out_manifest_name = new_hash + ".manifest"

    # The two possible files that can be generated with complete path:
    py_filepath = os.path.join(outdir, out_py_name)
    html_filepath = os.path.join(outdir, out_html_name)
    manifest_filepath = os.path.join(outdir, out_manifest_name)

    path_to_asn1scc = spawn.find_executable('asn1scc')

    if not path_to_asn1scc:
        raise TypeError('ASN.1 Compiler (asn1scc) not found in path')
    binary = path_to_asn1scc
    asn1scc_root = os.path.abspath(os.path.dirname(binary))
    # Fingerprint of the compiler, stored in the manifest of cache entries
    tool = _tool_fingerprint(binary)

    # call the ASN.1 compiler only if the cached files can be trusted
    py_content = None
    html_content = None
    if project_cache is None:
        LOG.info('No ASN.1 file in cache (or no cache folder)')
    else:
        reason, py_content, html_content = _check_cache(
                manifest_filepath,
                py_filepath,
                html_filepath if pprint else None,
                tool,
                input_hashes,
                key_options)
        if reason is None:
            LOG.info(f'Reusing cached ASN.1 modules from {py_filepath}')
        else:
            if os.path.exists(manifest_filepath):
                LOG.info(f'Not reusing the ASN.1 cache entry: {reason}')
            LOG.info('No ASN.1 file in cache (or no cache folder)')
            py_content = None
            html_content = None

    if py_content is None:
        LOG.debug(f"Python AST: {py_filepath}")
        stg = asn1scc_root + os.sep + 'python.stg'

        artifact_fds = {}
        if project_cache is not None:
            # The cache entry is about to be generated: remove any stale
            # files first (they may belong to another user of a shared cache
            # folder - writing through them would let that user choose the
            # content that is executed, and their manifest would vouch for
            # files that were replaced), then create the artifact files as
            # the current user and not writable by anyone else, so that
            # nobody can tamper with them during the generation window either
            _remove_stale_cache_entry(
                    [py_filepath, manifest_filepath]
                    + ([html_filepath] if pprint else []))
            artifact_fds = _precreate_cache_artifacts(
                    [py_filepath] + ([html_filepath] if pprint else []))
        if pprint:
            # Generate an html file with pretty-printed ASN.1 types.
            # The template is written in the output folder without ever
            # following a symbolic link (the name is fixed, so a link planted
            # in a shared cache folder could otherwise redirect the write)
            stg_qrc = QFile(':misc/pretty_print_asn1.stg')
            stg_qrc.open(QIODevice.ReadOnly)
            content = stg_qrc.readAll()
            stgfile = os.path.join(outdir, 'pretty_print_asn1.stg')
            if os.path.islink(stgfile):
                _remove_stale_cache_entry([stgfile])
            _write_file_checked(stgfile, bytes(content.data()))
            html = ['-customIcdUper', stgfile + '::' + html_filepath]
        else:
            html = []
        args = ['-customStgAstVersion', str(ast_version.value),
                '--field-prefix', 'AUTO',
                '-customStg', stg + '::' + py_filepath,
                '-renamePolicy', str(rename_policy.value)] + html + extraflags + file_list
        asn1scc = QProcess()
        LOG.debug(os.getcwd())
        LOG.debug(args)
        LOG.debug(binary + ' ' + ' '.join(args))
        asn1scc.start(binary, args)

        _ = waitfor_qprocess(asn1scc, "ASN.1 Compiler")
        # Read the generated files once, after the very same checks as for
        # a cached file. In a cache folder, the content is read through the
        # very descriptors of the files that this process created before
        # the generation: whatever happened at the paths in between (a file
        # replaced by another user, even one recycling the same inode
        # number) cannot make this code execute anything else than what
        # the compiler wrote through them
        try:
            py_content, reason = _read_generated_artifact(
                    py_filepath, artifact_fds.get(py_filepath))
            if reason is not None:
                raise TypeError(f'The generated ASN.1 module cannot be '
                                f'trusted: {reason}')
            if not py_content:
                raise TypeError(f'The ASN.1 compiler generated an empty '
                                f'module ("{py_filepath}")')
            html_content = None
            if pprint:
                html_content, reason = _read_generated_artifact(
                        html_filepath, artifact_fds.get(html_filepath))
                if reason is not None:
                    raise TypeError(f'The generated HTML file cannot be '
                                    f'trusted: {reason}')
                if not html_content:
                    raise TypeError(f'The ASN.1 compiler generated an empty '
                                    f'HTML file ("{html_filepath}")')
        finally:
            # The descriptors of the artifacts are not needed anymore,
            # whatever happened (the files themselves stay in the cache)
            for fd in artifact_fds.values():
                os.close(fd)
        if project_cache is not None:
            # Write the manifest last: an interrupted generation then leaves
            # no usable cache entry, and the next run regenerates it
            manifest = {'key_options': key_options,
                        'tool': tool,
                        'inputs': [[name, digest]
                                   for (name, _), digest
                                   in zip(inputs, input_hashes)],
                        'artifacts': {
                            'py': hashlib.sha256(py_content).hexdigest(),
                            'html': (hashlib.sha256(html_content)
                                     .hexdigest()
                                     if pprint else None)}}
            _write_manifest(manifest_filepath, manifest)
            # Make sure the new cache files are not group/world-writable
            artifacts = [py_filepath, manifest_filepath]
            if pprint:
                artifacts += [html_filepath, stgfile]
            _harden_cache_file_perms(artifacts)

    ast = _import_module_from_source(new_hash, py_filepath, py_content)
    AST[new_hash] = ast
    # In case the module was cached from asn1 files in other folders
    # fix the AST with the files from this project.
    ast.asn1Files = list(*files)
    if pprint:
        # add the (optionally-generated) pretty-printed HTML file
        try:
            ast.html = html_content.decode('utf-8')
        except UnicodeDecodeError as err:
            raise TypeError(f'The generated HTML file "{html_filepath}" is '
                            f'not valid UTF-8: {err}')
    else:
        ast.html = ''
    return ast

def create_choice_determinant_types(ast):
    ''' Postprocess the AST to add extra types corresponding to the CHOICE
        determinants. This allows the user to declare variables of these types,
        for local storage and comparison purposes.
        input: ast is the module generate by asn1scc. ast.types are the types 
        returns the newly created types (does not modify input AST)
    '''
    new_sorts = {}
    to_be_deleted = []
    for each in (sort for sort in ast.types.values()
                 if sort.type.kind == 'ChoiceType'):
        # we must capitalize the type here to remove any ambiguity
        new_sort_name = each.__name__.title() + '-Selection'
        choices = {key : type (key, (object,), {
            "IntValue": 0,
            "Line": each.Line,
            "CharPositionInLine": each.CharPositionInLine,
            "EnumID": each.type.Children[key].EnumID,
            #"IsStandardEnum" : False
            }) for key in each.type.Children.keys()
        }
        full_sort = \
                type(new_sort_name, (object,), {
                    "Line": each.Line,
                    "CharPositionInLine": each.CharPositionInLine,
                    "AddedType" : "True",
                    "ChoiceTypeName" : each.__name__,
                    "type": type(new_sort_name + "_type", (object,), {
                        "Line" : each.Line,
                        "CharPositionInLine": each.CharPositionInLine,
                        "kind": "EnumeratedType",
                        "Extensible": "False",
                        "ValuesAutoCalculated": "False",
                        "EnumValues": choices
                    })
                })

        # Check if an identical type name already exists. This is a problem
        # unless the enumerants are either the same or the same
        # with the suffix "_present" (meaning it is a type that
        # was generated by Opengeode (AdaGenerator). In that case we will
        # remove the existing type from the main AST and place the newly
        # created one instead (we must not have _present suffixes for the
        # parser to work properly, in particular with the present() operator)
        found = None
        for key in ast.types.keys():
            if key.lower() == new_sort_name.lower():
                found = key
                # here we could add a check that all enum values are identical
                # to the ones of the new type (with or without -present suffix)
                break
        if found is not None:
            # replace the content
            #ast.types[found] = full_sort
            #to_be_deleted.append(found)
            new_sorts[found] = full_sort
        else:
            new_sorts[new_sort_name] = full_sort
    for each in to_be_deleted:
        pass
        #ast.types.pop(each)
        #breakpoint()
        #ast.exportedTypes.pop(each)
    return new_sorts

def _dataview_key_file(tempdir):
    ''' Sidecar file that records the content key of the inputs from which
        the files of the output folder were generated (it replaces the
        previous timestamp-based staleness check) '''
    return os.path.join(tempdir, _DMT_PREFIX + '.inputs.sha256')


def _dataview_files_are_current(tempdir, dm_key):
    ''' Check that the files of the output folder are there and that they
        were generated from exactly these input files '''
    key_file = _dataview_key_file(tempdir)
    try:
        with open(key_file, 'r', encoding='utf-8') as source:
            recorded = source.read().strip()
    except OSError:
        return False
    if recorded != dm_key:
        return False
    for name in _DMT_MODULES:
        # DV_Types is not generated by all versions of the DMT tools
        if name == 'DV_Types':
            continue
        if not os.path.isfile(os.path.join(tempdir, name + '.py')):
            return False
    return True


def _import_dataview_modules(tempdir):
    ''' Import the modules generated by asn2dataModel by path, in import
        dependency order, and register them in sys.modules under their name:
        the generated code imports its siblings by name ("import DV",
        "from Stubs import ..."), and these statements must resolve to the
        modules of the current output folder, not to files of another
        folder. The content of each file is checked (not a symbolic link,
        owned by the current user) before it is executed, like a cache
        artifact. Returns a dict of the modules, keyed by module name. '''
    modules = {}
    for name in _DMT_MODULES:
        filepath = os.path.join(tempdir, name + '.py')
        if name == 'DV_Types' and not os.path.isfile(filepath):
            # Optional: imported by Stubs when the DMT tool generates it
            continue
        if not os.path.isfile(filepath):
            raise TypeError(f'asn2dataModel did not generate "{filepath}"')
        source, reason = _verify_cached_artifact(filepath, check_mode=False)
        if reason is not None:
            raise TypeError(f'The generated module "{filepath}" cannot be '
                            f'trusted: {reason}')
        modules[name] = _import_module_from_source(name, filepath, source)
    return modules


def _register_sibling_modules(modules):
    ''' Make sure the module names used by the generated code point to the
        modules of the dataview that was loaded last '''
    for name, module in modules.items():
        sys.modules[name] = module


def _create_database(asn1mod, db):
    ''' Create the SQL Alchemy database if the caller asked for one '''
    # db should be e.g. "sqlite:///file.sqlite"
    from sqlalchemy import create_engine
    engine = create_engine(db, echo=False)
    asn1mod.db_model.Base.metadata.create_all(engine)


def asn2dataModel(files, outdir=None, db=None):
    ''' Call asn2dataModel, including the Makefile.python and return
        the imported module "name_of_dataview_asn.py"
        From this module it is possible to create native Asn1scc instances of
        ASN.1 data types, and to access to DV.py, which contains constants
        such as the _PRESENT fields for choice selectors.
        In addition the SqlAlchemy interface is also imported
        give db a name to create the database
        if outdir is none, a temporary folder will be used
    '''
    assert len(files) > 0

    # Validate the input files before handing them over to the external
    # tools (cat, asn2dataModel, make), and read each of them once
    file_list = list(files)
    _validate_input_files(file_list)
    inputs = _read_input_files(file_list)

    # Key of this call: the number and content of the input files (not
    # their raw concatenation, so that no two different sets of files can
    # produce the same key) and the output folder. It identifies the
    # generated dataview (the previous, timestamp-based check could reuse a
    # stale set of files, and the previous fixed module name could return
    # the dataview of the first call to a caller that had changed its input
    # files).
    dm_hash = hashlib.sha256()
    for _, content in inputs:
        dm_hash.update(hashlib.sha256(content).hexdigest().encode('utf-8'))
    dm_hash.update((str(len(inputs)) + ':').encode('utf-8'))
    dm_hash.update(repr(outdir).encode('utf-8'))
    dm_key = dm_hash.hexdigest()

    if dm_key in ASN2DM:
        asn1mod, cached_dir, siblings = ASN2DM[dm_key]
        if _dataview_files_are_current(cached_dir, dm_key):
            LOG.info("Reusing DMT outputs from previous run")
            _register_sibling_modules(siblings)
            # Same input contents, but maybe not the same input paths
            asn1mod.asn1Files = file_list
            if db is not None:
                _create_database(asn1mod, db)
            return asn1mod
        LOG.info(f'DMT outputs in {cached_dir} do not match the input '
                 'files, regenerating them')

    # 1) Create the output folder: a temporary folder that will be removed
    #    when the process ends (the generated modules can still be used
    #    after this function returned), or the folder given by the caller
    #    (which is never removed)
    if '-g' in sys.argv:
        # In debug mode, don't hide the files in /tmp
        os.makedirs('./debug', exist_ok=True, mode=0o700)
        tempdir = './debug'
    elif outdir is None:
        tempdir = tempfile.mkdtemp()
        if tempdir not in _ASN2DM_TEMP_DIRS:
            _ASN2DM_TEMP_DIRS.add(tempdir)
            atexit.register(shutil.rmtree, tempdir, ignore_errors=True)
    else:
        os.makedirs(outdir, exist_ok=True, mode=0o700)
        tempdir = outdir

    concat_path = os.path.join(tempdir, _DMT_PREFIX)
    concat_file = concat_path + '.asn'
    reuse = _dataview_files_are_current(tempdir, dm_key)

    sys.path.insert(0, tempdir)
    try:
        if not reuse:
            # 2) Concat all input files to the output directory
            cat_bin = spawn.find_executable('cat')
            args = file_list  # list
            cat = QProcess()
            LOG.debug(os.getcwd())
            LOG.debug(cat_bin + ' ' + ' '.join(args))
            cat.start(cat_bin, args)
            merged = waitfor_qprocess(cat, 'Merge dataviews')
            # Both files below are written through a descriptor of the
            # current user that does not follow symbolic links: in an output
            # folder that the caller chose, a link could otherwise redirect
            # the write to any file of the user
            _write_file_checked(concat_file, bytes(merged.data()))
            # Record the content key of these inputs, so that the files of
            # the next run can be checked against it
            _write_file_checked(_dataview_key_file(tempdir),
                                dm_key.encode('utf-8'))

            # 3) Run asn2dataModel for Python
            asn2dm_bin = spawn.find_executable('asn2dataModel')
            args = ['-toPython', '-o', tempdir, concat_file]
            asn2dm = QProcess()
            LOG.debug(os.getcwd())
            LOG.debug(asn2dm_bin + ' ' + ' '.join(args))
            asn2dm.start(asn2dm_bin, args)
            waitfor_qprocess(asn2dm, 'DMT tool "asn2dataModel"')

            # 4) call make -f Makefile.python to build the .so
            make_bin = spawn.find_executable('make')
            args = ['-f', 'Makefile.python']
            make = QProcess()
            make.setWorkingDirectory(tempdir)
            LOG.debug(os.getcwd())
            LOG.debug(make_bin + ' ' + ' '.join(args))
            make.start(make_bin, args)
            waitfor_qprocess(make, 'make -f Makefile.python')

            # 5) Run asn2dataModel for the SQL Alchemy module
            args = ['-toSqlalchemy', '-o', tempdir, concat_file]
            asn2dm = QProcess()
            LOG.debug(os.getcwd())
            LOG.debug(asn2dm_bin + ' ' + ' '.join(args))
            asn2dm.start(asn2dm_bin, args)
            waitfor_qprocess(asn2dm, 'DMT tool "asn2dataModel"')
        else:
            LOG.info("Reusing DMT outputs from previous run")

        # 6) Import the generated modules by path (the output folder stays
        #    at the front of sys.path during the import, so that the
        #    modules that the generated code imports by name and that this
        #    function does not know about are still found there)
        siblings = _import_dataview_modules(tempdir)
        asn1mod = siblings[_DMT_PREFIX + '_asn']
        asn1mod.db_model = siblings['db_model']
        asn1mod.asn1Files = file_list
    finally:
        # Always restore sys.path, even if one of the tools failed above
        if sys.path and sys.path[0] == tempdir:
            sys.path.pop(0)
        else:
            try:
                sys.path.remove(tempdir)
            except ValueError:
                pass

    ASN2DM[dm_key] = (asn1mod, tempdir, siblings)
    # 7) Create the database if "db" is set
    if db is not None:
        _create_database(asn1mod, db)
    return asn1mod


if __name__ == '__main__':
    LOG.setLevel(logging.DEBUG)
    try:
        ast = parse_asn1(['dataview-uniq.asn'],
                          ast_version=ASN1.NoParameterizedTypes,
                          flags=[ASN1.AstOnly])
        print(ast.types.keys())
        sys.exit(0)
    except TypeError as err:
        print(str(err))
        sys.exit(1)
