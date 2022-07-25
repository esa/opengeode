include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) fce.pr system_structure.pr

test-parse:
	$(OPENGEODE) fce.pr system_structure.pr --check

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

test-ada: fce.ali

test-c: fce.c
	$(CC) -c fce.c

test-if:
	sdl2if fce.pr sytem_structure.pr

test-llvm: fce.o

coverage:
	coverage run -p $(OPENGEODE) fce.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
