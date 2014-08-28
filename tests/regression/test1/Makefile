include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

test-ada: og.ali

test-llvm: og.o

coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage