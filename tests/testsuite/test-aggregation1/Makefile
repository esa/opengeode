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

test-ada: dataview-uniq.o | test_ada.o
	cp challenge_ri.ada challenge_ri.adb
	$(OPENGEODE) challenge.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make challenge
	$(GNATBIND) -n challenge.ali
	$(GNATLINK) -o test_ada  test_ada.o challenge.ali -lm
	./test_ada | diff expected.log -

test-if:
	sdl2if challenge.pr system_structure.pr

challenge_datamodel.o: challenge_datamodel.asn dataview-uniq.asn
	$(ASN1SCC) -c -typePrefix asn1Scc -equal challenge_datamodel.asn dataview-uniq.asn
	$(CC) -O$(O) -c -g $*.c

test-c: challenge.c test_c.o dataview-uniq.o challenge_datamodel.o
	$(CC) challenge.c -c -o challenge.o
	$(CC) test_c.o challenge.c dataview-uniq.o challenge_datamodel.o -lm -o test_c
	./test_c | diff expected.log -

test-rust:
	$(OPENGEODE) challenge.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
