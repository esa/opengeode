include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) trafficlight.pr system_structure.pr

test-parse:
	$(OPENGEODE) trafficlight.pr system_structure.pr --check

test-ada:
	$(OPENGEODE) --toAda trafficlight.pr system_structure.pr
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c *.adb
	#$(CC) -c test.c
	#$(GNATBIND) -n trafficlight.ali
	#$(GNATLINK) -o testcase test.o trafficlight.ali -lgnat -lm

test-llvm:
	$(OPENGEODE) trafficlight.pr system_structure.pr --llvm
	$(LLC) trafficlight.ll
	$(CC) -c trafficlight.s

test-export:
	$(OPENGEODE) --png --pdf --svg trafficlight.pr system_structure.pr
	$(OPENGEODE) --png --pdf --svg --split trafficlight.pr system_structure.pr

coverage:
	coverage run -p $(OPENGEODE) trafficlight.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm test-exports coverage