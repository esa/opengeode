include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) fce.pr system_structure.pr

test-parse:
	$(OPENGEODE) fce.pr system_structure.pr --check

test-ada: fce.ali

test-llvm: fce.o

coverage:
	coverage run -p $(OPENGEODE) fce.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage