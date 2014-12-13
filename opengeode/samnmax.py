#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

'''
    This module was developed by Sam & Max
    https://raw.github.com/sametmax/Bat-belt/master/batbelt/hack.py
'''

import sys

from io import BytesIO
from contextlib import contextmanager


@contextmanager
def capture_ouput(stdout_to=None, stderr_to=None):
    """
        Context manager that captures any printed ouput in the 'with' block.

        :Exemple:

        >>> with capture_ouput() as (stdout, stderr):
        ...    print "hello",
        ...
        >>> print stdout.getvalue().upper()
        HELLO
        >>> with capture_ouput() as (stdout, stderr):
            # doctest: +IGNORE_EXCEPTION_DETAIL
        ...    assert False
        ...
        Traceback (most recent call last):
        AssertionError
        >>> from tempfile import NamedTemporaryFile
        >>> f = NamedTemporaryFile(mode="rw+b")
        >>> with capture_ouput(f) as (stdout, stderr):
        ...    print "hello",
        ...
        >>> print stdout.read()
        hello


        .. :warning: this is NOT thread safe.

        .. :note: The file like objects containing the capture are not closed
                  automatically by this context manager. You are responsible
                  to do it.

    It does not capture exception, so they bubble out and print the stack
    trace anyway.
    """

    try:

        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = c1 = stdout_to or BytesIO()
        sys.stderr = c2 = stderr_to or BytesIO()
        yield c1, c2

    finally:

        sys.stdout = stdout
        sys.stderr = stderr

        try:
            c1.flush()
            c1.seek(0)
        except (ValueError, TypeError):
            pass

        try:
            c2.flush()
            c2.seek(0)
        except (ValueError, TypeError):
            pass
