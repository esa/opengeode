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
	$(MAKE) -f Makefile.renaming
	cp test.ada code && cd code && gnat make test.ada && ./test | diff ../expected - || exit 1

test-c: 
	$(OPENGEODE) *.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) *.c -o test_c && ./test_c | diff expected -

test-if:
	sdl2if *.pr

test-llvm:
	$(warning llvm backend does not support this project)


coverage:
	coverage run -p $(OPENGEODE) *.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
