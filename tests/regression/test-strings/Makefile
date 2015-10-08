include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-ada: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali -lgnat
	./test_ada | diff - expected


test-c: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -O$(O) test_c.c og.c dataview-uniq.c -o test_c
	./test_c | diff - expected


test-llvm: test.o dataview-uniq.o | test_llvm.o
	$(OPENGEODE) og.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s
	$(CC) test.o dataview-uniq.o test_llvm.o -o test_llvm -lm


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
