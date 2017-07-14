include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-qgen-parse:
	$(TESTQGEN) og.pr

test-ada: dataview-uniq.o test_ada.o
	$(OPENGEODE) og.pr --toAda
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o dataview-uniq.o og.ali -lgnat
	./test_ada

test-c: 
	$(OPENGEODE) og.pr --toC
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) og.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
