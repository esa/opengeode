include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) operators.pr system_structure.pr

test-parse:
	$(OPENGEODE) operators.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) operators.pr system_structure.pr --check --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n operators.ali
	$(GNATLINK) test_ada.o operators.ali -lgnat -lm -o test_ada
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) operators.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(LLC) operators.ll
	$(CC) -c operators.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) operators.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) operators.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage