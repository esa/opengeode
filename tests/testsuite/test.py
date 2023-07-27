#!/usr/bin/env python3
import subprocess
import sys
import argparse
import time
import signal
from functools       import partial
from multiprocessing import cpu_count
from concurrent      import futures
import os

work1 = ['make', '-C']
work2 = ['make', '-C']
work3 = ['python', 'testqgen.py']

testsWork = {
    'all':               work1,
    'test-parse' :       work1,
    'test-qgen-parse' :  work1,
    'test-qgen-ada' :    work1,
    'test-qgen-c' :      work1,
    'test-qgen-gt-ada' : work1,
    'test-qgen-gt-c' :   work1,
    'test-ada' :         work1,
    'test-if' :          work1,
    'test-promela' :     work1,
    'test-c' :           work1,
    'test-llvm' :        work1,
    'test-vhdl':         work1
}


def openLog(name, mode='w'):
    logs = os.path.join(os.path.dirname(os.path.abspath(__file__)),'logs')
    os.makedirs(logs, exist_ok=True)
    return open(os.path.join(logs, name + '.err.txt'), mode)

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
    paths = sys.argv[2:]
    xfails = os.environ['EXPECTED_FAILURES']
    if op.rule in ['test-qgen-parse', 'test-qgen-ada', 'test-qgen-c', 'test-qgen-gt-ada', 'test-qgen-gt-c']:
        qgen_unsup = os.environ['QGEN_UNSUPPORTED']
    else:
        qgen_unsup = ""
    print ("Running {} tests using {} processors".format(len(paths), cpu_count()))

    with futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        fs = [executor.submit(partial(partial(make, op.rule)), path)
              for path in op.paths]
        # don't use the map function, because it keeps the order of
        # submission, meaning that even if a job finishes before the
        # previous one started, the log output will be delayed
        # use as_completed instead of map
        for each in futures.as_completed(fs):
            result = each.result()
            errcode, stdout, stderr, path, rule = result
            name = path.replace("/", "")
            print("(%3d / %3d) %50s: %s" %
                               (len(results)+1, len(paths),
                                name, colorMe(errcode,
                               '[OK]' if errcode==0 else
                                ('[EXPECTED FAILURE]'
                                if path in xfails
                                else ('[QGEN UNSUPPORTED]'
                                if path in qgen_unsup
                 else '[FAILED] ... build log in logs/{}.err'.format(name))))))
            sys.stdout.flush()
            if errcode != 0:
                # Failure: save the log immediately
                with openLog(name) as f:
                    f.write("=" * 80)
                    f.write("ERROR: %s %s" % (name, rule))
                    if stdout:
                        f.write("-- stdout " + "-" * 70)
                        f.write(stdout.decode())
                    if stderr:
                        f.write("-- stderr " + "-" * 70)
                        f.write(stderr.decode())
                        f.write("-" * 80)
            if errcode != 0 and name in xfails:
               # for "expected failures", set errcode to None
               result = (None, stdout, stderr, path, rule)
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
    expected_failures = 0
    for errcode, stdout, stderr, path, rule in results:
        if errcode == 0:
            continue
        if errcode is not None:
            failed += 1
        else:
            expected_failures += 1
    print("Finished in %.3fs" % elapsed)
    print("%s tests, %s errors" % (len(results), failed))
    print("%s expected failure(s)" % expected_failures)
    return 0 if not failed else 1


if __name__ == '__main__':
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ret = main()
    sys.stdout.write('\033[0m\n')
    sys.stdout.flush()
    sys.exit(ret)
