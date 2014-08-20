include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda og.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) og.pr system_structure.pr --llvm
	$(ASN1SCC) -c dataview-uniq.asn -equal -typePrefix asn1Scc
	$(LLC) og.ll
	$(CC) -c og.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage