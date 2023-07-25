include ../shared.mk

ROOT_MODEL=*.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) *.pr

test-parse:
	$(OPENGEODE) *.pr --check

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
	$(OPENGEODE) *.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make test_ada.ada
	./test_ada | diff expected -

test-c: 
	$(OPENGEODE) *.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn 
	$(CC) -O$(O) -o test_c *.c
	./test_c | diff expected -

test-if:
	sdl2if *.pr


test-llvm:
	$(OPENGEODE) *.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) *.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
