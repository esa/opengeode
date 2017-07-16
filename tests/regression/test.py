#!/usr/bin/env python3
import subprocess
import sys
import time
import signal
import os
from functools import partial
from multiprocessing import cpu_count
from concurrent import futures


def colorMe(result, msg):
    if sys.stdout.isatty():
        code = "1" if result else "2"
        msg = chr(27) + "[3" + code + "m" + msg + chr(27) + "[0m"
    return msg

def main():
    ''' Run the test cases in parallel on all available CPUs '''
    start = time.time()
    results = []
    rule = sys.argv[1]
    paths = sys.argv[2:]

    with futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        for result in executor.map(partial(make, rule), paths):
            print("%40s: %s" % (result[3], colorMe(result[0],
                               '[OK]' if result[0]==0 else '[FAILED]')))
            results.append(result)
        executor.map(partial(make, 'clean'), paths)
    sys.stdout.write('\n')

    elapsed = time.time() - start
    return summarize(results, elapsed)


def make(rule, path):
    ''' Call a Makefile with the required rule (e.g. test-ada or clean) '''
    proc = subprocess.Popen(
        ['make', '-C', path, rule],
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
            print(stdout.decode())
        if stderr:
            print("-- stderr " + "-" * 70)
            print(stderr.decode())
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
