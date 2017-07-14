include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-qgen-parse:
	$(TESTQGEN) og.pr

test-ada: 
	$(OPENGEODE) og.pr --toAda
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali

test-c: 
	$(OPENGEODE) og.pr --toC
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview.asn
	$(CC) -O$(O) -c *.c

test-python:
	$(OPENGEODE) og.pr --shared
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview.asn
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview.asn
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Llibog og
	$(GNATMAKE) -c -fPIC -gnat2012 b~og.adb
	$(CC) -shared -fPIC -o libog.so b~og.o og.o taste_dataview.o adaasn1rtl.o -lgnat
	python -c "from ctypes import *; test=CDLL('./libog.so'); test.liboginit()"

simu:
	$(OPENGEODE) og.pr --shared
	./og_simu.sh

test-llvm:
	$(OPENGEODE) og.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
