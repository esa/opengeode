#!/usr/bin/env python3
import sys, os, time, pexpect, subprocess
sys.path.append(os.path.abspath(".."))
import commonRegression

timeout = 15

expected = [
['''[INFO] Checking ['og.pr']''',
"[INFO] Parsing complete. Summary, found 0 warnings and 6 errors",
'''[ERROR] "a" is an IN parameter (read-only)''',
'''[ERROR] "so" is an IN parameter (read-only)''',
'''[ERROR] "ch" is an IN parameter (read-only)''',
'''[ERROR] "seq" is an IN parameter (read-only)''',
'''[ERROR] "seq" is an IN parameter (read-only)''',
'''[ERROR] "seq" is an IN parameter (read-only)'''
]]


result=commonRegression.test(
    ["opengeode --check og.pr"],
    expected, 
    timeout)
if 0!=result:
    sys.exit(1)
commonRegression.g_child.terminate(force=True)

