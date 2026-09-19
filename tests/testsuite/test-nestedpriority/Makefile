include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check 2>&1 | diff expected -

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

test-ada: test-parse

test-c: test-parse

test-if:
	sdl2if challenge.pr system_structure.pr

test-vhdl : test-parse

test-rust: test-parse
	@:

coverage:

.PHONY: all edit test-parse test-ada test-rust coverage
