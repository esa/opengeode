include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) --check orchestrator.pr system_structure.pr

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

test-ada: dataview-uniq.o | test_ada.o
	cp orchestrator_ri.ada orchestrator_ri.adb
	cp test_ada.ada test_ada.adb
	$(OPENGEODE) orchestrator.pr system_structure.pr --toAda
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make -g test_ada
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
