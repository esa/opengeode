include ../shared.mk

ROOT_MODEL=testsc.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) testsc.pr

test-parse:
	$(OPENGEODE) testsc.pr --check

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
	./check_simulation.sh && rm -rf testsc_simu

test-c: 
	$(OPENGEODE) testsc.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -c *.c

test-if:
	sdl2if testsc.pr

test-llvm:
	$(OPENGEODE) testsc.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s

coverage:
	coverage run -p $(OPENGEODE) testsc.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
