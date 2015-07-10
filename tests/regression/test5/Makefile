include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) function0.pr system_structure.pr

test-parse:
	$(OPENGEODE) function0.pr system_structure.pr --check

test-ada: function0.ali

test-c: function0.c
	$(CC) -c function0.c

test-llvm: function0.o

coverage:
	coverage run -p $(OPENGEODE) function0.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
