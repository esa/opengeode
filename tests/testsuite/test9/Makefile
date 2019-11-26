include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)

test-ada: challenge.ali

test-c: challenge.c
	$(CC) -c challenge.c

test-llvm: challenge.o

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
