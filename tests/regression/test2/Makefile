include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda orchestrator.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c orchestrator.adb

test-llvm:
	$(OPENGEODE) orchestrator.pr system_structure.pr --llvm
	$(LLC) orchestrator.ll
	$(CC) -c orchestrator.s

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage