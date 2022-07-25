include ../shared.mk

ROOT_MODEL=system_structure.pr

edit:
	$(OPENGEODE) function_in_sdl.pr system_structure.pr

test-parse:
	$(OPENGEODE) function_in_sdl.pr system_structure.pr --check

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

test-ada: function_in_sdl.ali dataview-uniq.o

test-c: function_in_sdl.c test_c.o dataview-uniq.o
	$(CC) function_in_sdl.c -c -o function_in_sdl.o
	$(CC) test_c.o function_in_sdl.c dataview-uniq.o -lm -o test_c
	./test_c 

test-if:
	sdl2if function_in_sdl.pr system_structure.pr


test-llvm: function_in_sdl.o

coverage:
	coverage run -p $(OPENGEODE) function_in_sdl.pr system_structure.pr --toAda

.PHONY: edit test-parse test-qgen-parse test-ada test-llvm coverage
