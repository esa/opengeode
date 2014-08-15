import os
import subprocess
import sys
import time


tests_folder = os.path.dirname(__file__)

paths = [
    'regression/test1',
    'regression/test2',
    'regression/test3',
    'regression/test4',
    'regression/test5',
    'regression/test6',
    'regression/test7',
    'regression/test8',
    'regression/test9',
    'regression/test10',
    'regression/test11',
    'regression/test12',
    'regression/test-controlflow',
    'regression/test-expressions',
    'regression/test-operators',
    'regression/test-substrings',
    'regression/test-exitnested',
]


def main():
    start = time.time()
    results = []

    for rule in sys.argv[1:]:
        for path in paths:
            full_path = os.path.join(tests_folder, path)
            result = make(full_path, rule)
            make(full_path, 'clean')
            results.append(result)
            sys.stdout.write('.' if result[0] == 0 else 'F')
            sys.stdout.flush()

    sys.stdout.write('\n')

    elapsed = time.time() - start
    sys.exit(summarize(results, elapsed))


def make(path, rule):
    proc = subprocess.Popen(
        ['make', '-C', path, rule],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    errcode = proc.wait()
    return (errcode, stdout, stderr, path, rule)


def summarize(results, elapsed):
    failed = 0
    for errcode, stdout, stderr, path, rule in results:
        if errcode == 0:
            continue
        failed += 1
        print "======================================================================"
        print "ERROR: %s %s" % (path, rule)
        if stdout:
            print "- stdout -------------------------------------------------------------"
            print stdout
        if stderr:
            print "- stderr -------------------------------------------------------------"
            print stderr
            print "----------------------------------------------------------------------"
    print "Finished in %.3fs" % elapsed
    print "%s tests, %s errors" % (len(results), failed)

    return 0 if not failed else 1


if __name__ == '__main__':
    main()
