include ../shared.mk

ROOT_MODEL=expression_based_decision.pr

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
	$(OPENGEODE) --toC --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO -uPER -ACN dataview-uniq.asn
	$(CC) -O$(O) -c *.c

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
