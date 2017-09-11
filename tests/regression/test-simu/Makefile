include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada: 
	mono $(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -c -g test_ada.c
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	mono $(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	mono $(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -c external_proc.c
	$(GNATMAKE) -O$(O) -gnat2012 -c *.adb
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o external_proc.o orchestrator.ali -lgnat
	./test_ada

simu:
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	taste-properties -s properties orchestrator.pr system_structure.pr
	make -f Makefile.properties
	./orchestrator_simu.sh


test-c:
	mono $(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -c -g test_c.c
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared --toC
	mono $(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -O$(O) test_c.c external_proc.c orchestrator.c -o test_c
	./test_c | diff - expected

test-llvm: orchestrator.o

test-python:
	$(OPENGEODE) orchestrator.pr system_structure.pr --shared
	mono $(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	mono $(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Lliborchestrator orchestrator
	$(GNATMAKE) -c -fPIC -gnat2012 b~orchestrator.adb
	$(CC) -c -fPIC external_proc.c
	$(CC) -shared -fPIC -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o external_proc.o -lgnat
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.liborchestratorinit()"

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
