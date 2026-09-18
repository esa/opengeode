# -*- coding: utf-8 -*-
"""pytest configuration for the tests of this folder.

New file (security-fix plan). It only makes sure that the tests import the
opengeode package of THIS repository, and nothing else.

Why this is needed: on machines where a stale, non-editable copy of the
opengeode package is physically present in the user's site-packages folder
(left over from an older "pip install"), a bare "import opengeode" run from
this folder resolves to that copy instead of the repository - Python finds
it in site-packages before the editable-install finder is consulted. The
tests of this folder verify the security fixes of the repository, so they
must exercise the code of the repository, not an arbitrary older copy of
it. Inserting the repository root at the front of sys.path before any
test module is imported guarantees that.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

if os.path.isdir(os.path.join(REPO_ROOT, 'opengeode')):
    if REPO_ROOT in sys.path:
        sys.path.remove(REPO_ROOT)
    sys.path.insert(0, REPO_ROOT)
