#!/usr/bin/env python3
"""Patch the RI stubs in generated Rust code for test-controlflow"""
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Make assert a no-op (matching Ada's null procedure)
old = 'fn ri_0_assert(res: &mut asn1SccBoolean, msg: &mut asn1SccCharString) { /* RI stub */ }'
new = 'fn ri_0_assert(_res: &mut asn1SccBoolean, _msg: &mut asn1SccCharString) {}'
content = content.replace(old, new)

# Make fail a no-op (matching Ada's null procedure)
old2 = 'fn ri_0_fail(msg: &mut asn1SccCharString) { /* RI stub */ }'
new2 = 'fn ri_0_fail(_msg: &mut asn1SccCharString) {}'
content = content.replace(old2, new2)

with open(sys.argv[1], 'w') as f:
    f.write(content)
