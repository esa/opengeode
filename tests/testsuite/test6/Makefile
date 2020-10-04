include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

test-parse:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

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
	cp myfunction_ri.ada myfunction_ri.adb
	$(OPENGEODE) myfunction.pr system_structure.pr --toAda
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make myfunction
	$(GNATBIND) -n myfunction.ali
	$(GNATLINK) -o test_ada test_ada.o myfunction.ali
	./test_ada | diff expected -

test-c: myfunction.c test_c.o dataview-uniq.o
	$(CC) myfunction.c -c -o myfunction.o
	$(CC) test_c.o myfunction.c -lm -o test_c
	./test_c | diff expected_c -

test-llvm: myfunction.o dataview-uniq.o | test_llvm.o
	$(CC) myfunction.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
