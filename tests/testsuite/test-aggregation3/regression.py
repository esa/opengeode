#!/usr/bin/env python3
import sys, os, time, pexpect, subprocess
sys.path.append(os.path.abspath(".."))
import commonRegression

timeout = 15

expected = [
    "Testing parallel states...",
    "[1] Startup",
    "[2] Entering  Parallel states",
    ["[-] State B starting", "[-] State A starting"],
    "[-] Received any_one",
    "[3] Action 1 START",
    "[-] Received any_one",
    "[4] Action 1 DONE",
    "[-] Received any_two",
    "[5] Action 2 START",
    "[-] Received any_two",
    "[6] Action 2 DONE",
    "[7] Quitting"
]

result=commonRegression.test(
    ["./test_ada"],
    expected, 
    timeout)
if 0!=result:
    sys.exit(1)
commonRegression.g_child.terminate(force=True)

