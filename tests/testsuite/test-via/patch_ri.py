#!/usr/bin/env python3
"""Implement pow RI for the via test (mirrors the Ada/C RI)."""
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace(
    'fn ri_0_pow(a: &mut asn1SccT_UInt32, b: &mut asn1SccT_UInt32, res: &mut asn1SccT_UInt32) { /* RI stub */ }',
    'fn ri_0_pow(a: &mut asn1SccT_UInt32, b: &mut asn1SccT_UInt32, res: &mut asn1SccT_UInt32) { *res = (*a as u64).pow(*b as u32) as asn1SccT_UInt32; }')
open(p, 'w').write(s)
