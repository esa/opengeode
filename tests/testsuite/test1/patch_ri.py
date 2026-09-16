#!/usr/bin/env python3
"""Patch the RI stubs in generated Rust code for test1"""
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Patch ri_0_rezult to print like the C test harness
old = 'fn ri_0_rezult(ze_rezult: &mut asn1SccMy_OctStr) { /* RI stub - implement me */ }'
new = '''fn ri_0_rezult(_ze_rezult: &mut asn1SccMy_OctStr) {
    println!("[C] got something]");
}'''
content = content.replace(old, new)

with open(sys.argv[1], 'w') as f:
    f.write(content)
