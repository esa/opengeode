include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) function2.pr system_structure.pr

test-parse:
	$(OPENGEODE) function2.pr system_structure.pr --check

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
	#make -f Makefile.function2
	$(OPENGEODE) function2.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make function2

test-c:
	$(OPENGEODE) function2.pr system_structure.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn 
	$(CC) -O$(O) -c *.c

test-if:
	sdl2if function2.pr


test-llvm:
	$(OPENGEODE) function2.pr system_structure.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) function2.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
