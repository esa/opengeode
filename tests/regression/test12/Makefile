include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) trafficlight.pr system_structure.pr

test-parse:
	$(OPENGEODE) trafficlight.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) trafficlight.pr system_structure.pr

test-ada: trafficlight.ali

test-c: trafficlight.c
	$(CC) trafficlight.c -c -o trafficlight.o

test-llvm: trafficlight.o

test-export:
	$(OPENGEODE) --png --pdf --svg trafficlight.pr system_structure.pr
	$(OPENGEODE) --png --pdf --svg --split trafficlight.pr system_structure.pr

coverage:
	coverage run -p $(OPENGEODE) trafficlight.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm test-exports coverage
