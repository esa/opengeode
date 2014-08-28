include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) controlflow.pr system_structure.pr

test-parse:
	$(OPENGEODE) controlflow.pr system_structure.pr --check

test-ada: controlflow.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n controlflow.ali
	$(GNATLINK) test_ada.o controlflow.ali -lgnat -lm -o test_ada
	./test_ada | diff expected -

test-llvm: controlflow.o dataview-uniq.o | test_llvm.o
	$(CC) controlflow.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) controlflow.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage