include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) flight.pr system_structure.pr

test-parse:
	$(OPENGEODE) flight.pr system_structure.pr --check

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

test-ada: flight.ali

test-c: flight.c
	$(CC) -include missing.h -c flight.c

test-if:
	sdl2if flight.pr system_structure.pr

test-llvm: flight.o

coverage:
	coverage run -p $(OPENGEODE) flight.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
