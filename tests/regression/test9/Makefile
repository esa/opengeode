include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda challenge.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c challenge.adb

test-llvm:
	$(OPENGEODE) challenge.pr system_structure.pr --llvm
	$(LLC) challenge.ll
	$(CC) -c challenge.s

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage