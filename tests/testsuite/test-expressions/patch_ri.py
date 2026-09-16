#!/usr/bin/env python3
"""Patch the RI stub in generated Rust code for test-expressions"""
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = 'fn ri_0_assert(res: &mut asn1SccBoolean, msg: &mut asn1SccCharString) { /* RI stub */ }'
new = '''fn ri_0_assert(res: &mut asn1SccBoolean, msg: &mut asn1SccCharString) {
    let s: String = msg.arr.iter().map(|b| *b as char).collect();
    if *res { println!("PASS: {}", s); }
    else { println!("FAIL: {}", s); }
}'''

content = content.replace(old, new)
with open(sys.argv[1], 'w') as f:
    f.write(content)
