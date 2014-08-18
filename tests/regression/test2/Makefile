include ../shared.mk

all: test-ada test-llvm

edit:
	../../../opengeode.py orchestrator.pr system_structure.pr

test-parse:
	../../../opengeode.py orchestrator.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda orchestrator.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c orchestrator.adb

test-llvm:
	../../../opengeode.py orchestrator.pr system_structure.pr --llvm
	llc orchestrator.ll
	gcc -c orchestrator.s

coverage:
	coverage run -p ../../../opengeode.py orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage