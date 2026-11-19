#!/usr/bin/env python3
"""Implement the RI stubs of the orchestrator test in Rust (mirrors the Ada RI)."""
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace(
    'fn ri_0_VESAT_one_step(vesat_input: &mut asn1SccT_GNC_LV_SIM_INPUTS) { /* RI stub - implement me */ }',
    'fn ri_0_VESAT_one_step(_vesat_input: &mut asn1SccT_GNC_LV_SIM_INPUTS) { println!("VESAT One Step called"); }')
open(p, 'w').write(s)
