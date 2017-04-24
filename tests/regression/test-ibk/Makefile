include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) packetmanager.pr system_structure.pr

test-parse:
	$(OPENGEODE) packetmanager.pr system_structure.pr --check

test-ada: packetmanager.ali

test-c: packetmanager.c
	$(CC) -c packetmanager.c

test-llvm: packetmanager.o

coverage:
	coverage run -p $(OPENGEODE) packetmanager.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
