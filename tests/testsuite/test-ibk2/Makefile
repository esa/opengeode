include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) framemanager.pr system_structure.pr

test-parse:
	$(OPENGEODE) framemanager.pr system_structure.pr --check

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

test-ada: framemanager.ali

test-c: framemanager.c
	$(CC) -c framemanager.c

test-if:
	sdl2if framemanager.pr system_structure.pr

test-llvm: framemanager.o

coverage:
	coverage run -p $(OPENGEODE) framemanager.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
