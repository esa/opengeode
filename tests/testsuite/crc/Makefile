include ../shared.mk

ROOT_MODEL=insdl.pr system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) ${ROOT_MODEL}

test-parse:
	$(OPENGEODE) ${ROOT_MODEL} --check

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
	#make -f Makefile.og
	$(OPENGEODE) ${ROOT_MODEL} --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make insdl

test-c:
	$(OPENGEODE) insdl.pr system_structure.pr --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -c *.c

test-rust:
	$(OPENGEODE) insdl.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

test-if:
	sdl2if ${ROOT_MODEL}


coverage:
	coverage run -p $(OPENGEODE) ${ROOT_MODEL} --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
