include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) operators.pr system_structure.pr

test-parse:
	$(OPENGEODE) operators.pr system_structure.pr --check

test-ada: operators.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n operators.ali
	$(GNATLINK) test_ada.o operators.ali -lgnat -lm -o test_ada
	./test_ada | diff expected -

test-c: operators.c test_c.o dataview-uniq.o
	$(CC) -include missing.h operators.c -c -o operators.o
	$(CC) test_c.o operators.o -lm -o test_c
	./test_c | diff expected_c -

test-llvm: operators.o dataview-uniq.o | test_llvm.o
	$(CC) operators.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) operators.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
