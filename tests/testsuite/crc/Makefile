include ../shared.mk

ROOT_MODEL=insdl.pr system_structure.pr

all: test-ada test-llvm

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
	$(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn 
	$(CC) -O$(O) -c *.c

test-if:
	sdl2if ${ROOT_MODEL}

test-llvm:
	$(OPENGEODE) insdl.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) ${ROOT_MODEL} --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
