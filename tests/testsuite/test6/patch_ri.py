#!/usr/bin/env python3
"""Implement the RI/timer stubs of test6 in Rust (mirrors the C driver)."""
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace(
    'fn ri_0_result_data(titi: &mut asn1SccT_Int32) { /* RI stub - implement me */ }',
    'fn ri_0_result_data(titi: &mut asn1SccT_Int32) { println!("[C] result_data: {}", *titi); }')
s = s.replace(
    'fn set_myTimer(val: &mut asn1SccT_UInt32) { /* timer stub */ }',
    'fn set_myTimer(val: &mut asn1SccT_UInt32) { println!("[C] SET MyTimer: {}", *val); }')
s = s.replace(
    'fn reset_myTimer() { /* timer stub */ }',
    'fn reset_myTimer() { println!("RESET MyTimer"); }')
open(p, 'w').write(s)
