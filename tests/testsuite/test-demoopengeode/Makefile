include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check || echo [OK]

test-ada: 
	$(OPENGEODE) orchestrator.pr system_structure.pr --check || echo [OK]

test-c:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check && 

test-if:
	sdl2if orchestrator.pr system_structure.pr


test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
