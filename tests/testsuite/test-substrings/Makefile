include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

test-parse:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

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

test-ada: myfunction.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n myfunction.ali
	$(GNATLINK) -o test_ada test_ada.o myfunction.ali
	./test_ada | diff expected -

test-c: myfunction.c | test_ada.o
	$(CC) -g -o test_c myfunction.c test_c.c
	./test_c | diff expected -

test-if:
	sdl2if myfunction.pr system_structure.pr

test-rust:
	$(OPENGEODE) myfunction.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
