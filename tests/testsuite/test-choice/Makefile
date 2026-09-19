include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

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
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada  -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) test_ada.ada && ./test_ada | diff expected_ada -

test-c: 
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -g -o test_c *.c && ./test_c | diff expected_c -

test-if:
	sdl2if og.pr



coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

test-rust:
	$(OPENGEODE) og.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

.PHONY: all edit test-parse test-ada test-rust coverage
