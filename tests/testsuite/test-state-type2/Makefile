include ../shared.mk

ROOT_MODEL=foo.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) foo.pr

test-parse:
	$(OPENGEODE) foo.pr --check

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
	cp ris.ada ris.ads && cp ris_adb.ada ris.adb
	gnat make test_ada.ada
	./test_ada | diff expected -

test-simu:
	$(MAKE) clean
	$(OPENGEODE) *.pr --taste --simu --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	cp ris.ada ris.ads && cp ris_adb.ada ris.adb
	cp foo_ri.ada foo_ri.ads
	gnat make -g test_simu.ada
	./test_simu

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

clean:
	find . -maxdepth 1 -type f \
		! -name "dv.asn" \
		! -name "foo.pr" \
		! -name "Makefile" \
		! -name "expected" \
		! -name "test_ada.ada" \
		! -name "ris.ada" \
		! -name "ris_adb.ada" \
		! -name "test_c.c" \
		! -name "foo_ri.ada" \
		! -name "test_simu.ada" \
		-delete
	rm -rf x86
.PHONY: all edit test-parse test-ada test-llvm coverage
