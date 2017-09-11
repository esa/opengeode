include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada: orchestrator.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada

test-c: orchestrator.c test_c.o dataview-uniq.o
	$(CC) -include missing.h orchestrator.c -c -o orchestrator.o
	$(CC) test_c.o orchestrator.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected -

test-llvm: orchestrator.o

test-python:
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	mono $(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n -Lliborchestrator orchestrator
	$(GNATMAKE) -c b~orchestrator.adb
	$(CC) -shared -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o -lgnat
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.liborchestratorinit()"

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
