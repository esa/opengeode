include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) expressions.pr system_structure.pr

test-parse:
	$(OPENGEODE) expressions.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) expressions.pr system_structure.pr --check --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n expressions.ali
	$(GNATLINK) test_ada.o expressions.ali -lgnat -lm -o test_ada
	./test_ada

test-llvm:
	$(OPENGEODE) expressions.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(LLC) expressions.ll
	$(CC) -c expressions.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) expressions.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

coverage:
	coverage run -p $(OPENGEODE) expressions.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage