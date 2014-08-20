include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) function0.pr system_structure.pr

test-parse:
	$(OPENGEODE) function0.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda function0.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c function0.adb

test-llvm:
	$(OPENGEODE) function0.pr system_structure.pr --llvm
	$(LLC) function0.ll
	$(CC) -c function0.s

coverage:
	coverage run -p $(OPENGEODE) function0.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage