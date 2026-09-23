include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) trafficlight.pr system_structure.pr

test-parse:
	$(OPENGEODE) trafficlight.pr system_structure.pr --check

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

test-ada: trafficlight.ali

test-c: trafficlight.c
	$(CC) trafficlight.c -c -o trafficlight.o

test-if:
	sdl2if trafficlight.pr system_structure.pr

test-export:
	$(OPENGEODE) --png --pdf --svg trafficlight.pr system_structure.pr
	$(OPENGEODE) --png --pdf --svg --split trafficlight.pr system_structure.pr

test-rust:
	$(OPENGEODE) trafficlight.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) trafficlight.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-exports coverage test-rust
