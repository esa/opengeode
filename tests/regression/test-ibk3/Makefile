include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) node.pr system_structure.pr

test-parse:
	$(OPENGEODE) node.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) node.pr system_structure.pr

test-ada: node.ali

test-c: node.c
	$(CC) -c node.c

test-llvm: node.o

coverage:
	coverage run -p $(OPENGEODE) node.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
