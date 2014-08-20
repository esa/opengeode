include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) fce.pr system_structure.pr

test-parse:
	$(OPENGEODE) fce.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda fce.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c fce.adb

test-llvm:
	$(OPENGEODE) fce.pr system_structure.pr --llvm
	$(LLC) fce.ll
	$(CC) -c fce.s

coverage:
	coverage run -p $(OPENGEODE) fce.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage