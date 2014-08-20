include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda og.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c og.adb

test-llvm:
	$(OPENGEODE) og.pr system_structure.pr --llvm
	$(LLC) og.ll
	$(CC) -c og.s

coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage