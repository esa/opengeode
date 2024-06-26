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

test-ada:
	$(OPENGEODE) orchestrator.pr system_structure.pr --toAda
	#$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	#$(CC) -c -g test_ada.c
	#$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn orchestrator_datamodel.asn
	#$(CC) -c external_proc.c
	#$(GNATMAKE) -O$(O) -gnat2012 -c *.adb
	#$(GNATBIND) -n orchestrator.ali
	#$(GNATLINK) -o test_ada test_ada.o external_proc.o orchestrator.ali
	#./test_ada

simu:
	rm -rf orchestrator_simu
	$(OPENGEODE) orchestrator.pr system_structure.pr --toAda
	taste-properties -s properties orchestrator.pr system_structure.pr
	make -f Makefile.properties
	./orchestrator_simu.sh

test-c:
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	#$(CC) -c -g test_c.c
	$(OPENGEODE) orchestrator.pr system_structure.pr --toC
	gcc -c *.c
	#$(CC) -O$(O) test_c.c external_proc.c orchestrator.c -o test_c
	#./test_c | diff - expected

test-if:
	sdl2if orchestrator.pr system_structure.pr

test-llvm: orchestrator.o

test-python:
	$(OPENGEODE) orchestrator.pr system_structure.pr
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Lliborchestrator orchestrator
	$(GNATMAKE) -c -fPIC -gnat2012 b~orchestrator.adb
	$(CC) -c -fPIC external_proc.c
	$(CC) -shared -fPIC -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o external_proc.o
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.liborchestratorinit()"

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage simu
