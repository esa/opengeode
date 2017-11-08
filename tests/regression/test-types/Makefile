include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) function1.pr system_structure.pr

test-parse:
	$(OPENGEODE) function1.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) function1.pr system_structure.pr

test-ada: function1.ali

test-c: function1.c

test-llvm: function1.o

coverage:
	coverage run -p $(OPENGEODE) function1.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
