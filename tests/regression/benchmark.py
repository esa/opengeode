import os
import subprocess
import sys
import time as t

from tabulate import tabulate


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
        "name": testfolder[:-1],
        "size": {
            "ada": size(llvm_bin),
            "llvm": size(ada_bin),
        },
        "time": {
            "ada": time(ada_bin),
            "llvm": time(llvm_bin),
        }
    }

    return result


def size(file):
    call(["strip", os.path.abspath(file)])
    return os.path.getsize(file)


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

    print "Summary"
    print "-------"
    print ""
    print "Size: Ada %.2f%% LLVM %.2f%%" % diff([r["size"] for r in results])
    print "Time: Ada %.2f%% LLVM %.2f%%" % diff([r["time"] for r in results])
    print ""

    headers = ["Benchmark", "Ada size (B)", "LLVM size (B)", "Ada time (us)", "LLVM time (us)"]
    table = []
    for result in results:
        table.append([
            result["name"],
            result["size"]["ada"],
            result["size"]["llvm"],
            int(round(result["time"]["ada"] * (10 ** 6))),
            int(round(result["time"]["llvm"] * (10 ** 6))),
        ])

    print tabulate(table, headers, tablefmt="orgtbl")

    return 0 if results and not errors else 1


def diff(results):
    return 100, mean(([float(r["llvm"]) / float(r["ada"]) * 100 for r in results]))


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
