include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr

test-parse:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --check

test-ada: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda
	

test-c: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toC

test-llvm:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --llvm -O$(O)


coverage:
	coverage run -p $(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
