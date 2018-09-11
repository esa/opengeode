#!/usr/bin/env python3
import subprocess
import sys
import argparse
import time
import signal
from functools import partial
from multiprocessing import cpu_count
from concurrent import futures
import os

work1 = ['make', '-C']
work2 = ['make', '-C']
work3 = ['python', 'testqgen.py']

testsWork = {
'all': work1, 
'test-parse' : work1,
'test-qgen-parse' : work1,
'test-qgen-ada' : work1,
'test-qgen-c' : work1,
'test-qgen-gt-ada' : work1,
'test-qgen-gt-c' : work1,
'test-ada' : work1,
'test-c' : work1,
'test-llvm' : work1,
'test-vhdl': work1
}

def colorMe(result, msg):
    if sys.stdout.isatty():
        code = "1" if result else "2"
        msg = chr(27) + "[3" + code + "m" + msg + chr(27) + "[0m"
    return msg

def parse_args():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument('rule', metavar='Rule', type=str)
    parser.add_argument('paths', metavar='Path', type=str, nargs='+')
    parser.add_argument('-u', '--update', action='store_true')
    return parser.parse_args()

def main():
    ''' Run the test cases in parallel on all available CPUs '''
    start = time.time()
    results = []
    op = parse_args()
    xfails = os.environ['EXPECTED_FAILURES']
    qgen_unsup = os.environ['QGEN_UNSUPPORTED']
    with futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        for result in executor.map(partial(partial(make, op.rule)), op.paths):
            print("%40s: %s" % (result[3], colorMe(result[0],
                               '[OK]' if result[0]==0 else
                                ('[EXPECTED FAILURE]' 
                                if result[3] in xfails
                                else ('[QGEN UNSUPPORTED]' 
                                if result[3] in qgen_unsup
                                else '[FAILED]')))))
            results.append(result)
        executor.map(partial(make, 'clean'), op.paths)
    sys.stdout.write('\n')

    elapsed = time.time() - start
    return summarize(results, elapsed)


def make(rule, path):
    ''' Call a Makefile with the required rule (e.g. test-ada or clean) '''

    ''' Choose work settings based on the given rule '''
    work=testsWork[rule]

    ''' Compose the command based on the rule'''
    cmd=[work[0], work[1], path, rule]

    proc = subprocess.Popen(
      cmd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )

    stdout, stderr = proc.communicate()
    errcode = proc.wait()

    return (errcode, stdout, stderr, path, rule)


def summarize(results, elapsed):
    ''' At the end display the errors of project that failed '''
    failed = 0
    for errcode, stdout, stderr, path, rule in results:
        if errcode == 0:
            continue
        failed += 1
        print("=" * 80)
        print("ERROR: %s %s" % (path, rule))
        if stdout:
            print("-- stdout " + "-" * 70)
            print(stdout.decode("latin-1"))
        if stderr:
            print("-- stderr " + "-" * 70)
            print(stderr.decode("latin-1"))
            print("-" * 80)
    print("Finished in %.3fs" % elapsed)
    print("%s tests, %s errors" % (len(results), failed))

    return 0 if not failed else 1


if __name__ == '__main__':
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ret = main()
    sys.stdout.write('\033[0m\n')
    sys.stdout.flush()
    sys.exit(ret)
