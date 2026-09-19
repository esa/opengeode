include ../shared.mk

ROOT_MODEL=*.pr

all: test-ada

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
	$(ASN1SCC) -Ada  -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n spacecraft.ali

test-c: 
	$(OPENGEODE) *.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -c *.c

test-if:
	sdl2if *.pr



test-rust:
	$(OPENGEODE) *.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) *.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
