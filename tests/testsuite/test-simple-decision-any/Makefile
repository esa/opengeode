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
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n complexsdl.ali

test-c:
	$(OPENGEODE) --toC --dumpAST $(ROOT_MODEL) 2>&1 | sort | diff expected_c - || exit 0

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
