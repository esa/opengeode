import os
import subprocess
import sys
import time as t


def main():
    start = t.time()
    results = []
    errors = 0
    for testfolder in sys.argv[1:]:
        result = benchmark(testfolder)
        make(testfolder, 'clean')
        if result:
            results.append(result)
        else:
            errors += 1
        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\n')

    elapsed = t.time() - start
    sys.exit(summarize(results, errors, elapsed))


def benchmark(testfolder):
    for rule in ("test-llvm", "test-ada"):
        if make(testfolder, rule) != 0:
            return

    llvm_bin = os.path.join(testfolder, "test_ada")
    ada_bin = os.path.join(testfolder, "test_llvm")

    for bin_name in (llvm_bin, ada_bin):
        if not os.path.isfile(bin_name):
            return

    result = {
        "size": {
            "ada": os.path.getsize(llvm_bin),
            "llvm": os.path.getsize(ada_bin),
        },
        "time": {
            "ada": time(ada_bin),
            "llvm": time(llvm_bin),
        }
    }

    return result


def time(file, iters=1000):
    start = t.time()
    call(["/bin/bash", "-c", "for i in {1..%s} ; do %s ; done" % (iters, file)])
    return (t.time() - start) / iters


def summarize(results, errors, elapsed):
    print "Finished in %.3fs" % elapsed
    print "%s benchmarks, %s errors" % (len(results) + errors, errors)

    if not results:
        print "No results"
        return 1

    print "Summary:"
    print "  Size: Ada %.2f%% LLVM %.2f%%" % diff(results, "size")
    print "  Time: Ada %.2f%% LLVM %.2f%%" % diff(results, "time")

    return 0 if results and not errors else 1


def diff(results, metric):
    metrics = [r[metric] for r in results]
    return 100, mean(([float(m["llvm"]) / float(m["ada"]) * 100 for m in metrics]))


def mean(values):
    return sum(values) / len(values)


def make(path, rule):
    return call(["make", "-C", path, rule])[0]


def call(args):
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    errcode = proc.wait()
    return (errcode, stdout, stderr)


if __name__ == '__main__':
    main()
