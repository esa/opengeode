include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) expressions.pr system_structure.pr

test-parse:
	$(OPENGEODE) expressions.pr system_structure.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)
	cd generated_ada && cp ../test_qgen_ada.c test_qgen_ada.c; \
		mono $(ASN1SCC) -c -typePrefix asn1Scc -equal ../dataview-uniq.asn; \
		$(GNATBIND) -n obj_ada/expressions.ali; \
		$(CC) -O$(O) -c -g test_qgen_ada.c ; \
		$(GNATLINK) -o test_qgen_ada test_qgen_ada.o obj_ada/expressions.ali -lm; \
		./test_qgen_ada

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)
	cd generated_c && cp ../test_qgen_c.c test_qgen_c.c; \
		$(CC) -O$(O) -c -g test_qgen_c.c; \
		$(CC) test_qgen_c.o obj/*.o -lm -o test_qgen_c; \
		./test_qgen_c

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)
	cd generated_gt_c && cp ../test_qgen_gt_c.c test_qgen_c.c; \
		$(CC) -O$(O) -c -g test_qgen_c.c; \
		$(CC) test_qgen_c.o obj/*.o -lm -o test_qgen_c; \
		./test_qgen_c

test-ada: expressions.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n expressions.ali
	$(GNATLINK) test_ada.o expressions.ali -lm -o test_ada
	./test_ada

test-c: expressions.c test_c.o dataview-uniq.o
	$(CC) expressions.c -c -o expressions.o
	$(CC) test_c.o dataview-uniq.o expressions.o -lm -o test_c
	./test_c

test-llvm: expressions.o dataview-uniq.o | test_llvm.o
	$(CC) expressions.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

test-vhdl : test-c
	bambu expressions.c test_c.c dataview-uniq.c --experimental-setup=BAMBU -v4

coverage:
	coverage run -p $(OPENGEODE) expressions.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
