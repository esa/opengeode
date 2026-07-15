include ../shared.mk

ROOT_MODEL=decision_any.pr

all: test-ada test-c

edit:
	$(OPENGEODE) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) $(ROOT_MODEL) --check

test-ada:
	$(OPENGEODE) --toAda --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	cp -f complexsdl_ri.ada complexsdl_ri.adb
	$(GNATMAKE) -O$(O) -o test_ada test_ada.ada
	./test_ada

test-c:
	$(OPENGEODE) --toC --dumpAST $(ROOT_MODEL) 2>&1 | sort | diff expected_c -
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -g -o test_c complexsdl.c test_c.c dataview-uniq.c
	./test_c

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
