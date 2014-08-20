include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

test-parse:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda myfunction.pr system_structure.pr || exit 1
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc
	$(GNATMAKE) -c myfunction.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n myfunction.ali
	$(GNATLINK) -o test_ada test_ada.o myfunction.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) myfunction.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -equal -typePrefix asn1Scc
	$(LLC) myfunction.ll
	$(CC) -c myfunction.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) myfunction.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage