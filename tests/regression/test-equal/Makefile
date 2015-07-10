include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

test-ada: og.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali -lgnat
	./test_ada | diff expected -

test-c: og.c test_c.o dataview-uniq.o
	$(CC) og.c -c -o og.o
	$(CC) test_c.o og.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected -


test-llvm: og.o dataview-uniq.o | test_llvm.o
	$(CC) og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

test-vhdl : test-c
	bambu og.c test_c.c --experimental-setup=BAMBU

coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
