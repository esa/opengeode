include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) function1.pr system_structure.pr

test-parse:
	$(OPENGEODE) function1.pr system_structure.pr --check

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

test-ada: function1.ali

test-c: function1.c

test-if:
	sdl2if function1.pr sytem_structure.pr

test-llvm: function1.o

coverage:
	coverage run -p $(OPENGEODE) function1.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
