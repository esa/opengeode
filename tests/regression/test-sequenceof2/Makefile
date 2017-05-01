include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) test.pr

test-parse:
	$(OPENGEODE) test.pr --check

test-ada: 
	$(OPENGEODE) test.pr --toAda
	$(ASN1SCC) -Ada dataview.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n test.ali
	gnat make test_ada.ada

simu:
	$(OPENGEODE) test.pr --shared
	./test_simu.sh

test-c: 
	$(OPENGEODE) test.pr --toC
	$(ASN1SCC) -c dataview.asn -typePrefix asn1Scc -equal
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) test.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) test.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage simu
