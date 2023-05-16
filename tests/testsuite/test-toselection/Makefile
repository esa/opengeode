include ../shared.mk

ROOT_MODEL=spacecraft.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) spacecraft.pr

test-parse:
	$(OPENGEODE) spacecraft.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)

test-ada: 
	$(OPENGEODE) spacecraft.pr --toAda
	$(ASN1SCC) -Ada  -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n spacecraft.ali

test-c: 
	$(OPENGEODE) spacecraft.pr --toC
	$(ASN1SCC) -c  -typePrefix asn1Scc -equal dataview.asn
	$(CC) -O$(O) -c *.c

test-if:
	sdl2if spacecraft.pr


test-llvm:
	$(OPENGEODE) spacecraft.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) spacecraft.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
