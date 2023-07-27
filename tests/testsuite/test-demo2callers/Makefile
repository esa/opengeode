include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) f1.pr system_structure.pr

test-parse:
	$(OPENGEODE) f1.pr system_structure.pr --check

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

test-ada: f1.ali
	cp check.ada check.adb && cp ris.ada ris.ads && \
	$(GNATMAKE) -O$(O) -gnat2012 -g -fprofile-arcs -ftest-coverage check.adb && \
	./check | diff expected - && echo "[TEST] OK"

test-c: f1.c test_c.o dataview-uniq.o
	$(CC) f1.c -c -o f1.o
	$(CC) test_c.o f1.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected -

test-if:
	sdl2if f1.pr system_structure.pr

test-llvm: f1.o dataview-uniq.o | test_llvm.o
	$(CC) f1.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

coverage:
	coverage run -p $(OPENGEODE) f1.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
