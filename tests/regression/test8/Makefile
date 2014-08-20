include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) --check orchestrator.pr system_structure.pr

test-ada:
	$(OPENGEODE) --toAda orchestrator.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(LLC) orchestrator.ll
	$(CC) -c orchestrator.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) orchestrator.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage