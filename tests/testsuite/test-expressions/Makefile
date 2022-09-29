include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) expressions.pr system_structure.pr

test-parse:
	$(OPENGEODE) expressions.pr system_structure.pr --check

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

test-ada: test_ada.adb expressions.adb
	gnat make test_ada
	./test_ada | diff expected -

expressions.adb: expressions.pr expressions_ri.adb
	$(OPENGEODE) expressions.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn

test_ada.adb: test_ada.ada
	cp test_ada.ada test_ada.adb

expressions_ri.adb: expressions_ri.ada
	cp expressions_ri.ada expressions_ri.adb

test-c: expressions.c test_c.o dataview-uniq.o
	$(CC) expressions.c -c -o expressions.o
	$(CC) test_c.o dataview-uniq.o expressions.o -lm -o test_c
	./test_c

test-if:
	sdl2if expressions.pr system_structure.pr

test-llvm: expressions.o dataview-uniq.o | test_llvm.o
	$(CC) expressions.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

test-vhdl : test-c
	bambu expressions.c test_c.c dataview-uniq.c --experimental-setup=BAMBU -v4

coverage:
	coverage run -p $(OPENGEODE) expressions.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
