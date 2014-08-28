include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada: orchestrator.ali

test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage