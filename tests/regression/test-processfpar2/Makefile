include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-qgen-parse:
	$(TESTQGEN) og.pr

test-ada:
	$(OPENGEODE) og.pr --toAda

test-c:
	$(OPENGEODE) og.pr --toC


test-llvm:
	$(OPENGEODE) og.pr --llvm -O$(O)


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
