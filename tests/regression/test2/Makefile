include ../shared.mk

ROOT_MODEL=system_structure.pr

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN) orchestrator.pr system_structure.pr

test-ada: orchestrator.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada
	#gcov orchestrator.adb

test-c: orchestrator.c test_c.o dataview-uniq.o
	$(CC) orchestrator.c -c -o orchestrator.o
	$(CC) test_c.o orchestrator.c dataview-uniq.o -lm -o test_c
	./test_c 


test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: edit test-parse test-qgen-parse test-ada test-llvm coverage
