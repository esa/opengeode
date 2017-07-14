include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-qgen-parse:
	$(TESTQGEN) og.pr

test-ada: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toAda
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali -lgnat
	./test_ada | diff - expected


test-c: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toC
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn
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
