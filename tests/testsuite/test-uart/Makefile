include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada test-llvm

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
	cp og_ri.ada og_ri.adb
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	cp ris.ada ris.ads && cp check.ada check.adb && cp ris_adb.ada ris.adb
	gnat make -g -O0 check
	./check | diff expected -

test-c:
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -o test_c *.c
	./test_c | diff expected -

test-if:
	sdl2if og.pr

test-llvm:
	$(OPENGEODE) og.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
