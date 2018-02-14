include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) f1.pr system_structure.pr

test-parse:
	$(OPENGEODE) f1.pr system_structure.pr --check

test-ada: f1.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n f1.ali
	$(GNATLINK) -o test_ada test_ada.o dataview-uniq.o f1.ali -lgnat
	./test_ada
	#gcov f1.adb

test-c: f1.c test_c.o dataview-uniq.o
	$(CC) f1.c -c -o f1.o
	$(CC) test_c.o f1.c dataview-uniq.o -lm -o test_c
	./test_c | diff expected -


test-llvm: f1.o dataview-uniq.o | test_llvm.o
	$(CC) f1.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm


coverage:
	coverage run -p $(OPENGEODE) f1.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
