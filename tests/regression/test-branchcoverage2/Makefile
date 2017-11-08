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
	$(TESTQGEN) myfunction.pr system_structure.pr

test-ada:
	$(OPENGEODE) --toAda myfunction.pr system_structure.pr 2>&1 | sort | diff expected - || exit 0

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit check test-parse test-ada coverage