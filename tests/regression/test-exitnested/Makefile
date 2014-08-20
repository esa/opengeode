include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda challenge.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c *.adb
	$(CC) -c test_ada.c
	$(GNATBIND) -n challenge.ali
	$(GNATLINK) -o test_ada  test_ada.o challenge.ali -lgnat -lm
	./test_ada | diff expected -

test-llvm:
	$(OPENGEODE) challenge.pr system_structure.pr --check --llvm
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(LLC) challenge.ll
	$(CC) -c challenge.s
	$(CC) -c dataview-uniq.c
	$(CC) -c test_llvm.c
	$(CC) challenge.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage