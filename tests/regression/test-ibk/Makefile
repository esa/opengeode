include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) packetmanager.pr system_structure.pr

test-parse:
	$(OPENGEODE) packetmanager.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-ada: packetmanager.ali

test-c: packetmanager.c
	$(CC) -c packetmanager.c

test-llvm: packetmanager.o

coverage:
	coverage run -p $(OPENGEODE) packetmanager.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
