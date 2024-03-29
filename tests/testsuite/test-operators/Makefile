include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) operators.pr system_structure.pr

test-parse:
	$(OPENGEODE) operators.pr system_structure.pr --check

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

test-ada: operators.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n operators.ali
	$(GNATLINK) test_ada.o operators.ali -lm -o test_ada
	./test_ada | diff expected -

test-c: operators.c test_c.o dataview-uniq.o
	$(CC) -g operators.c -c asn1crt.c
	$(CC) -g test_c.o operators.o asn1crt.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected_c -

test-if:
	sdl2if operators.pr system_structure.pr

test-llvm: operators.o dataview-uniq.o | test_llvm.o
	$(CC) operators.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) operators.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
