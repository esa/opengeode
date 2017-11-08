include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

test-parse:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) myfunction.pr system_structure.pr

test-ada: myfunction.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n myfunction.ali
	$(GNATLINK) -o test_ada test_ada.o myfunction.ali -lgnat
	./test_ada | diff expected -

test-c: myfunction.c | test_ada.o
	$(CC) -o test_c myfunction.c test_c.c
	./test_c | diff expected -

test-llvm: myfunction.o dataview-uniq.o | test_llvm.o
	$(CC) myfunction.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage