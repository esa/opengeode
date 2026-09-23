include ../shared.mk

ROOT_MODEL=DemoDeviceDSAP_fixed.pr

all: test-ada

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

test-qgen-gt-ada:
	$(TESTQGEN_GT_ADA) $(ROOT_MODEL)

test-qgen-gt-c:
	$(TESTQGEN_GT_C) $(ROOT_MODEL)

test-ada: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda

test-c:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toC

test-rust:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

test-if:
	sdl2if DemoDeviceDSAP_fixed.pr

coverage:
	coverage run -p $(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
