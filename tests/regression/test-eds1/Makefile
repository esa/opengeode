include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) testsc.pr

test-parse:
	$(OPENGEODE) testsc.pr --check

test-ada: 
	./check_simulation.sh && rm -rf testsc_simu

test-c: 
	$(OPENGEODE) testsc.pr --toC
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview.asn
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) testsc.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) testsc.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
