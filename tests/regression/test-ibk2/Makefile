include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) framemanager.pr system_structure.pr

test-parse:
	$(OPENGEODE) framemanager.pr system_structure.pr --check

test-ada: framemanager.ali

test-c: framemanager.c
	$(CC) -c framemanager.c

test-llvm: framemanager.o

coverage:
	coverage run -p $(OPENGEODE) framemanager.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
