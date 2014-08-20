include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) controlflow.pr system_structure.pr

test-parse:
	$(OPENGEODE) controlflow.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) controlflow.pr system_structure.pr --check --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n controlflow.ali
	$(GNATLINK) test_ada.o controlflow.ali -lgnat -lm -o test_ada
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) controlflow.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(LLC) controlflow.ll
	$(CC) -c controlflow.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) controlflow.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) controlflow.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage