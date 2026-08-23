#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenGEODE - Model Monitor & File Lock Manager

Provides file locking (detecting concurrent instances) and periodic external
modification monitoring for OpenGEODE model files using Python standard libraries.

Copyright (c) 2012-2026 European Space Agency
"""

import os
import sys
import json
import time
import socket
import getpass
import atexit
import logging

LOG = logging.getLogger(__name__)


def is_pid_running(pid: int) -> bool:
    """Check if a process with the given PID is currently running."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError as err:
            import errno
            if err.errno == errno.EPERM:
                # Process exists but owned by another user
                return True
            return False


def get_lock_filepath(filepath: str) -> str:
    """Return the lock file path corresponding to a model file."""
    filepath = os.path.abspath(filepath)
    dirname, filename = os.path.split(filepath)
    return os.path.join(dirname, f".{filename}.lock")


class ModelLockManager:
    """Manages file locks to prevent / warn about concurrent model access."""

    def __init__(self):
        self.acquired_locks = set()
        atexit.register(self.release_locks)

    def check_lock(self, filepath: str):
        """
        Check if a file is locked by another running process.
        Returns (is_locked, lock_info_dict_or_None).
        If a lock is stale (process dead), the stale lock file is removed.
        """
        if not filepath:
            return False, None

        lock_path = get_lock_filepath(filepath)
        if not os.path.exists(lock_path):
            return False, None

        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                lock_info = json.load(f)
        except Exception as err:
            LOG.warning(f"Could not read lock file {lock_path}: {err}. Removing stale lock.")
            self._remove_lock_file(lock_path)
            return False, None

        lock_pid = lock_info.get("pid")
        if lock_pid == os.getpid():
            # Current process owns this lock
            return False, None

        if lock_pid and is_pid_running(lock_pid):
            return True, lock_info

        # Process is dead -> stale lock file
        LOG.info(f"Removing stale lock file {lock_path} (PID {lock_pid} is no longer running)")
        self._remove_lock_file(lock_path)
        return False, None

    def acquire_lock(self, filepath: str) -> bool:
        """Create lock file for the given model file."""
        if not filepath:
            return False

        lock_path = get_lock_filepath(filepath)
        lock_info = {
            "pid": os.getpid(),
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "filepath": os.path.abspath(filepath),
        }

        try:
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump(lock_info, f, indent=2)
            self.acquired_locks.add(lock_path)
            LOG.debug(f"Acquired lock for {filepath} -> {lock_path}")
            return True
        except Exception as err:
            LOG.error(f"Failed to create lock file {lock_path}: {err}")
            return False

    def release_lock(self, filepath: str):
        """Release lock for a single file."""
        if not filepath:
            return
        lock_path = get_lock_filepath(filepath)
        self._remove_lock_file(lock_path)
        self.acquired_locks.discard(lock_path)

    def release_locks(self):
        """Release all lock files created by this instance."""
        locks_to_remove = list(self.acquired_locks)
        for lock_path in locks_to_remove:
            self._remove_lock_file(lock_path)
        self.acquired_locks.clear()

    def _remove_lock_file(self, lock_path: str):
        try:
            if os.path.exists(lock_path):
                os.remove(lock_path)
                LOG.debug(f"Released lock file {lock_path}")
        except Exception as err:
            LOG.error(f"Error removing lock file {lock_path}: {err}")


class FileMonitor:
    """Tracks modification timestamps of loaded files to detect external changes."""

    def __init__(self):
        self.tracked_files = {}

    def track_files(self, file_paths):
        """Set or update tracked files."""
        self.tracked_files.clear()
        for path in file_paths:
            self.add_file(path)

    def add_file(self, filepath: str):
        """Add a file to monitoring."""
        if not filepath:
            return
        abspath = os.path.abspath(filepath)
        if os.path.exists(abspath):
            try:
                self.tracked_files[abspath] = os.path.getmtime(abspath)
            except OSError as err:
                LOG.warning(f"Could not stat file {abspath}: {err}")

    def update_file(self, filepath: str):
        """Update tracked mtime after save."""
        if not filepath:
            return
        abspath = os.path.abspath(filepath)
        if os.path.exists(abspath):
            try:
                self.tracked_files[abspath] = os.path.getmtime(abspath)
            except OSError:
                pass

    def stop_tracking(self):
        """Clear all tracked files."""
        self.tracked_files.clear()

    def check_modifications(self):
        """
        Check tracked files for external modifications.
        Returns a list of (filepath, old_mtime, new_mtime) for modified files.
        """
        modified = []
        for abspath, old_mtime in list(self.tracked_files.items()):
            if os.path.exists(abspath):
                try:
                    current_mtime = os.path.getmtime(abspath)
                    if current_mtime > old_mtime + 1e-3:
                        modified.append((abspath, old_mtime, current_mtime))
                except OSError:
                    pass
        return modified
