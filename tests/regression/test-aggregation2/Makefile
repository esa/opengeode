include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-ada: 
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali

test-c: 
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(CC) -O$(O) -c *.c


test-llvm:
	$(OPENGEODE) og.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s

test-python:
	$(OPENGEODE) og.pr --shared
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(ASN1SCC) -c dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Llibog og
	$(GNATMAKE) -c -fPIC -gnat2012 b~og.adb
	$(CC) -shared -fPIC -o libog.so b~og.o og.o adaasn1rtl.o taste_dataview.o -lgnat
	python -c "from ctypes import *; test=CDLL('./libog.so'); test.liboginit(); test.og_for_a(); test.og_for_b(); test.og_for_a(); test.og_for_b()"


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
