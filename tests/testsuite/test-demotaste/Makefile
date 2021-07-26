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
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada: 
	$(OPENGEODE) orchestrator.pr system_structure.pr --toAda
	asn1scc -Ada -typePrefix asn1Scc -equal *.asn
	gnat make -gnatd.E orchestrator

test-c:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check && 


test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
