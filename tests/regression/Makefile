DISABLED_TESTS=test-branchcoverage/
TEST_CASES=$(filter-out $(DISABLED_TESTS), $(sort $(dir $(wildcard */))))

DISABLED_BENCHMARKS=test1/ test2/ test3/ test4/ test5/ test6/ test7/ test9/ \
                    test12/ test-branchcoverage/
BENCHMARK_CASES=$(filter-out $(DISABLED_BENCHMARKS), $(sort $(dir $(wildcard */))))

test-parse:
	@python test.py test-parse $(TEST_CASES)

test-ada:
	@python test.py test-ada $(TEST_CASES)

test-c:
	@python test.py test-c $(TEST_CASES)

test-llvm:
	@python test.py test-llvm $(TEST_CASES)

test-vhdl:
	@python test.py test-c $(TEST_CASES)

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

.PHONY: test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 coverage clean
