include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check 2>&1 | grep ERROR | wc | grep "1       9      61" && echo OK

test-ada: test-parse

test-c: test-parse

test-llvm: test-parse

test-vhdl : test-parse

coverage:

.PHONY: all edit test-parse test-ada test-llvm coverage
