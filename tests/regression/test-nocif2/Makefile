include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr

test-parse:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --check

test-ada: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda
	$(ASN1SCC) -Ada dv.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n DemoDeviceDSAP_fixed.ali

test-c: 
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --toC
	$(ASN1SCC) -c dv.asn -typePrefix asn1Scc -equal
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) DemoDeviceDSAP_fixed.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) DemoDeviceDSAP_fixed.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
