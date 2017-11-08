include ../shared.mk

ROOT_MODEL=DemoDeviceDSAP_fixed.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr

test-parse:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --check

test-qgen-parse:
	$(TESTQGEN_PARSE) $(ROOT_MODEL)

test-qgen-ada:
	$(TESTQGEN_ADA) $(ROOT_MODEL)

test-qgen-c:
	$(TESTQGEN_C) $(ROOT_MODEL)

test-ada: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda
	

test-c: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toC

test-llvm:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --llvm -O$(O)


coverage:
	coverage run -p $(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
