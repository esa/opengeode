include ../shared.mk

ROOT_MODEL=system_structure.pr

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)
	cd generated_ada && cp ../test_qgen_ada.c test_ada.c; \
		$(GNATBIND) -n obj_ada/challenge.ali; \
		$(CC) -O$(O) -c -g test_ada.c ; \
		$(GNATLINK) -o test_ada test_ada.o obj_ada/challenge.ali -lgnat -lm; \
		./test_ada

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)
	
test-qgen-ada-asn:
	$(TESTQGEN_ADA_ASN) $(ROOT_MODEL)

test-qgen-c-asn:
	$(TESTQGEN_C_ASN) $(ROOT_MODEL)

test-ada: challenge.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n challenge.ali
	$(GNATLINK) -o test_ada  test_ada.o challenge.ali -lgnat -lm
	./test_ada

test-c: challenge.c test_c.o dataview-uniq.o
	$(CC) -include missing.h challenge.c -c -o challenge.o
	$(CC) test_c.o challenge.c dataview-uniq.o -lm -o test_c
	./test_c

test-llvm: challenge.o dataview-uniq.o | test_llvm.o
	$(CC) challenge.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
