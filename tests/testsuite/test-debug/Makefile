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

test-c: orchestrator.c test_c.o dataview-uniq.o
	$(CC) -include missing.h orchestrator.c -c -o orchestrator.o
	$(CC) test_c.o dataview-uniq.o orchestrator.o -lm -o test_c
	./test_c | diff expected -

test-llvm: orchestrator.o

test-python:
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(GNATMAKE) -O$(O) -gnat2012 -c -fPIC *.adb
	$(GNATBIND) -n -Lliborchestrator orchestrator
	$(GNATMAKE) -c -fPIC -gnat2012 b~orchestrator.adb
	$(CC) -shared -fPIC -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.liborchestratorinit()"

test-vhdl : test-c
	bambu orchestrator.c test_c.c --experimental-setup=BAMBU

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
