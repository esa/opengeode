import argparse
import os
import string
import subprocess
import sys
import time as t

from tabulate import tabulate


def main():
    options = parse_args()

    start = t.time()
    results = []

    for testfolder in options.testfolders:
        results.append(benchmark(testfolder, options.optimization))
        make(testfolder, 'clean')
        sys.stdout.write('.')
        sys.stdout.flush()

    print ("")

    elapsed = t.time() - start
    sys.exit(summarize(results, elapsed, options))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-O", dest="optimization", metavar="level", type=int,
            action="store", choices=[0, 1, 2, 3], default=0,
            help="set optimization level")
    parser.add_argument('testfolders', metavar='testfolder', type=str, nargs='*',
            help='test folder(s)')
    return parser.parse_args()


def benchmark(testfolder, opt_level):
    result = {
        "name": testfolder[:-1],
    }

    for rule in ("test-llvm", "test-ada"):
        if make(testfolder, rule, "O=%d" % opt_level) != 0:
            result["status"] = "ERROR"
            return result

    llvm_bin = os.path.join(testfolder, "test_llvm")
    ada_bin = os.path.join(testfolder, "test_ada")

    for bin_name in (llvm_bin, ada_bin):
        if not os.path.isfile(bin_name):
            result["status"] = "ERROR"
            return result

    result.update({
        "status": "OK",
        "size": {
            "ada": size(ada_bin),
            "llvm": size(llvm_bin),
        },
        "time": {
            "ada": time(ada_bin),
            "llvm": time(llvm_bin),
        }
    })

    return result


def size(file):
    call(["strip", os.path.abspath(file)])
    return os.path.getsize(file)


def time(file, iters=1000):
    start = t.time()
    call(["/bin/bash", "-c", "for i in {1..%s} ; do %s ; done" % (iters, file)])
    return (t.time() - start) / iters


def summarize(results, elapsed, options):
    print ("")
    print ("Summary")
    print ("-------")
    print ("")

    max_name_len = max([len(r["name"]) for r in results]) + 3
    num_errors = 0
    valid_results = []

    for r in results:
        print("%s [%s]" % (string.ljust(r["name"], max_name_len, '.'), r["status"]))
        if r["status"] == "OK":
            valid_results.append(r)
        else:
            num_errors += 1

    print ("")
    print ("Finished in %.3fs" % elapsed)
    print ("%s benchmarks, %s errors" % (len(results), num_errors))
    print ("")

    if not valid_results:
        print ("No results")
        return 1

    if options.optimization != 0:
        print ("Optimization level: %d" % options.optimization)
        print ("")
    print ("Size: Ada %.2f%% LLVM %.2f%%" % diff([r["size"] for r in valid_results]))
    print ("Time: Ada %.2f%% LLVM %.2f%%" % diff([r["time"] for r in valid_results]))
    print ("")

    headers = ["Benchmark", "Ada size (B)", "LLVM size (B)", "Ada time (us)", "LLVM time (us)"]
    table = []
    for r in valid_results:
        table.append([
            r["name"],
            r["size"]["ada"],
            r["size"]["llvm"],
            int(round(r["time"]["ada"] * (10 ** 6))),
            int(round(r["time"]["llvm"] * (10 ** 6))),
        ])

    print (tabulate(table, headers, tablefmt="orgtbl"))

    return 0 if num_errors == 0 else 1


def diff(results):
    return 100, mean(([float(r["llvm"]) / float(r["ada"]) * 100 for r in results]))


def mean(values):
    return sum(values) / len(values)


def make(path, rule, *args):
    call_args = ["make", "-C", path, rule]
    call_args.extend(args)
    return call(call_args)[0]


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
