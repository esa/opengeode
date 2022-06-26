include ../shared.mk

ROOT_MODEL=controller.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) controller.pr system_structure.pr

test-parse:
	$(OPENGEODE) controller.pr system_structure.pr --check

simu:
	$(OPENGEODE) --shared controller.pr system_structure.pr
	rm -rf controller_simu
	mkdir -p controller_simu
	cp *.png controller_simu
	cp UserWidgets.py controller_simu
	./controller_simu.sh

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)

test-ada: 
	$(OPENGEODE) controller.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn 

test-c: 
	$(OPENGEODE) controller.pr system_structure.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn 
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) controller.pr system_structure.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) controller.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage simu
