include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

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

test-ada: challenge.ali

test-c: challenge.c
	$(CC) -c challenge.c

test-if:
	sdl2if challenge.pr sytem_structure.pr

test-rust:
	$(OPENGEODE) challenge.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada coverage test-rust
