include ../shared.mk

ROOT_MODEL=test.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) test.pr

test-parse:
	$(OPENGEODE) test.pr --check

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
	$(OPENGEODE) test.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n test.ali
	gnat make test_ada.ada

test-if:
	sdl2if test.pr

simu:
	$(OPENGEODE) test.pr --shared
	./test_simu.sh

test-c: 
	$(OPENGEODE) test.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) test.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) test.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage simu
