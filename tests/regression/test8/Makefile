include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) --check orchestrator.pr system_structure.pr

test-qgen-parse:
	$(TESTQGEN) orchestrator.pr system_structure.pr

test-ada: orchestrator.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada | diff expected -

test-c: orchestrator.c test_c.o dataview-uniq.o
	$(CC) orchestrator.c -c -o orchestrator.o
	$(CC) test_c.o orchestrator.c dataview-uniq.o -lm -o test_c
	./test_c | diff expected_c -

test-llvm: orchestrator.o dataview-uniq.o | test_llvm.o
	$(CC) orchestrator.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
