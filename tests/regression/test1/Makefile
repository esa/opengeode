include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

test-ada: og.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali -lgnat
	./test_ada


test-llvm: og.o dataview-uniq.o | test_llvm.o
	$(CC) og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm


coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
