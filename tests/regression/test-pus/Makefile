include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) flight.pr system_structure.pr

test-parse:
	$(OPENGEODE) flight.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) flight.pr system_structure.pr

test-ada: flight.ali

test-c: flight.c
	$(CC) -include missing.h -c flight.c

test-llvm: flight.o

coverage:
	coverage run -p $(OPENGEODE) flight.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
