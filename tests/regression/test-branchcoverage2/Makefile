include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

check:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

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

test-ada:
	$(OPENGEODE) --toAda myfunction.pr system_structure.pr 2>&1 | sort | diff expected - || exit 0

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit check test-parse test-ada coverage