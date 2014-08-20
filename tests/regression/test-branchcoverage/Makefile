include ../shared.mk

all: test-ada

edit:
	$(OPENGEODE) myfunction.pr system_structure.pr

check:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

test-parse:
	$(OPENGEODE) myfunction.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda myfunction.pr system_structure.pr 2>&1 | sort | diff expected - || exit 0

coverage:
	coverage run  -p $(OPENGEODE) myfunction.pr system_structure.pr --toAda

.PHONY: all edit check test-parse test-ada coverage