#!/usr/bin/env python3
"""Implement the uart RIs in Rust (mirrors the C driver)."""
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace(
    'fn ri_0_send_to_uart(send_to_uart_param: &mut asn1SccOctStr) { /* RI stub - implement me */ }',
    'fn ri_0_send_to_uart(send_to_uart_param: &mut asn1SccOctStr) { println!("Received  {}", send_to_uart_param.n_count); }')
# The model provides its own check_queue in C; here we give the runtime stub a body.
s = s.replace(
    'pub unsafe extern "C" fn og_check_queue(res: &mut bool) {\n    // Provided by runtime\n}',
    'pub unsafe extern "C" fn og_check_queue(res: &mut bool) {\n    println!("Checking queue");\n    *res = false;\n}')
open(p, 'w').write(s)
