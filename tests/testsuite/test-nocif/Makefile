include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

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

test-ada: orchestrator.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali
	./test_ada

test-c:
	$(OPENGEODE) --toC orchestrator.pr system_structure.pr 2>&1 | sort | diff expected_c - || exit 0

test-if:
	sdl2if orchestrator.pr system_structure.pr

test-llvm: orchestrator.o

test-python:
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n -Lliborchestrator orchestrator
	$(GNATMAKE) -c b~orchestrator.adb
	$(CC) -shared -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.liborchestratorinit()"

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
