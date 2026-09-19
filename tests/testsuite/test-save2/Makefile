include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

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
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n og.ali

test-c:
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -c *.c

test-rust:
	$(OPENGEODE) og.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

test-if:
	sdl2if og.pr

test-python:
	$(OPENGEODE) og.pr --shared
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview.asn
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Llibog og
	$(GNATMAKE) -c -fPIC -gnat2012 b~og.adb
	$(CC) -shared -fPIC -o libog.so b~og.o og.o taste_dataview.o adaasn1rtl.o
	python -c "from ctypes import *; test=CDLL('./libog.so'); test.liboginit()"

simu:
	$(OPENGEODE) og.pr --shared
	./og_simu.sh


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
