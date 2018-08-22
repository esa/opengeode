DISABLED_TESTS=test-branchcoverage/
TEST_CASES=$(filter-out $(DISABLED_TESTS), $(sort $(dir $(wildcard */))))

DISABLED_BENCHMARKS=test1/ test2/ test3/ test4/ test5/ test6/ test7/ test9/ \
                    test12/ test-branchcoverage/
BENCHMARK_CASES=$(filter-out $(DISABLED_BENCHMARKS), $(sort $(dir $(wildcard */))))

export EXPECTED_FAILURES=test-typecheck/ test-procedure/ test-demoopengeode/

test-parse:
	@python3 test.py test-parse $(TEST_CASES)

test-qgen-parse:
	@python3 test.py test-qgen-parse $(TEST_CASES)

test-qgen-ada:
	@python3 test.py test-qgen-ada $(TEST_CASES)

test-qgen-c:
	@python3 test.py test-qgen-c $(TEST_CASES)

test-qgen-gt-ada:
	@python3 test.py test-qgen-gt-ada $(TEST_CASES)

test-qgen-gt-c:
	@python3 test.py test-qgen-gt-c $(TEST_CASES)

test-ada:
	@python3 test.py test-ada $(TEST_CASES)

test-c:
	@python3 test.py test-c $(TEST_CASES)

test-llvm:
	@python3 test.py test-llvm $(TEST_CASES)

test-vhdl:
	@python3 test.py test-c $(TEST_CASES)

benchmark:
	@python benchmark.py $(BENCHMARK_CASES)

benchmark-O1:
	@python benchmark.py $(BENCHMARK_CASES) -O1

benchmark-O2:
	@python benchmark.py $(BENCHMARK_CASES) -O2

benchmark-O3:
	@python benchmark.py $(BENCHMARK_CASES) -O3

coverage:
	@for v in $(TEST_CASES) ; \
		do $(MAKE) -C $$v coverage && mv $$v/.coverage* . || exit 1 ; \
	done
	@coverage combine

clean:
	@for v in $(TEST_CASES) ; \
		do $(MAKE) -s -C $$v clean ; \
	done

.PHONY: test-parse test-qgen-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 coverage clean
