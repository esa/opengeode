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

    # NOTE: the LLVM backend was removed from OpenGEODE (out of date).
    # The benchmark now measures the Ada backend only.
    for rule in ("test-ada",):
        if make(testfolder, rule, "O=%d" % opt_level) != 0:
            result["status"] = "ERROR"
            return result

    ada_bin = os.path.join(testfolder, "test_ada")

    for bin_name in (ada_bin,):
        if not os.path.isfile(bin_name):
            result["status"] = "ERROR"
            return result

    result.update({
        "status": "OK",
        "size": {
            "ada": size(ada_bin),
        },
        "time": {
            "ada": time(ada_bin),
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

    headers = ["Benchmark", "Ada size (B)", "Ada time (us)"]
    table = []
    for r in valid_results:
        table.append([
            r["name"],
            r["size"]["ada"],
            int(round(r["time"]["ada"] * (10 ** 6))),
        ])

    print (tabulate(table, headers, tablefmt="orgtbl"))

    return 0 if num_errors == 0 else 1


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
