include ../shared.mk

all: test-ada test-llvm

edit:
	../../../opengeode.py function0.pr system_structure.pr

test-parse:
	../../../opengeode.py function0.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda function0.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c function0.adb

test-llvm:
	../../../opengeode.py function0.pr system_structure.pr --llvm
	llc function0.ll
	gcc -c function0.s

coverage:
	coverage run -p ../../../opengeode.py function0.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage