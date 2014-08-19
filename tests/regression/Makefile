TEST_CASES = \
	test1 \
	test2 \
	test3 \
	test4 \
	test5 \
	test6 \
	test7 \
	test8 \
	test9 \
	test10 \
	test11 \
	test12 \
	test-controlflow \
	test-exitnested \
	test-expressions \
	test-operators \
	test-substrings \

BENCHMARK_CASES = \
	test8 \
	test9 \
	test10 \
	test11 \
	test-controlflow \
	test-exitnested \
	test-expressions \
	test-operators \
	test-substrings \

test-parse:
	@python test.py test-parse $(TEST_CASES)

test-ada:
	@python test.py test-ada $(TEST_CASES)

test-llvm:
	@python test.py test-llvm $(TEST_CASES)

benchmark:
	@python benchmark.py $(BENCHMARK_CASES)
	@make clean

coverage:
	for v in $(TEST_CASES) ; do make -C $$v coverage && mv $$v/.coverage* . \
	|| exit 1 ; done ; coverage combine

clean:
	for v in $(TEST_CASES); do make -C $$v clean ; done

.PHONY: test-parse test-ada test-llvm benchmark coverage clean
