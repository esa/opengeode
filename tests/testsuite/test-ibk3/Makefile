include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) node.pr system_structure.pr

test-parse:
	$(OPENGEODE) node.pr system_structure.pr --check

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

test-ada: node.ali

test-c: node.c
	$(CC) -c node.c

test-if:
	sdl2if node.pr system_structure.pr

test-llvm: node.o

coverage:
	coverage run -p $(OPENGEODE) node.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
