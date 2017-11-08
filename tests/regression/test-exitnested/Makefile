include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

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

test-ada: challenge.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n challenge.ali
	$(GNATLINK) -o test_ada  test_ada.o challenge.ali -lgnat -lm
	./test_ada | diff expected -

test-c: challenge.c test_c.o dataview-uniq.o
	$(CC) challenge.c -c -o challenge.o
	$(CC) test_c.o dataview-uniq.o challenge.o -lm -o test_c
	./test_c
	./test_c | diff expected -

test-llvm: challenge.o dataview-uniq.o | test_llvm.o
	$(CC) challenge.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

test-vhdl : test-c
	bambu challenge.c test_c.c --experimental-setup=BAMBU

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
