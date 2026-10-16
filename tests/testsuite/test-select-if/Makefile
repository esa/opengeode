include ../shared.mk

ROOT_MODEL=foo.pr

all: test-ada

edit:
	$(OPENGEODE) foo.pr

test-parse:
	$(OPENGEODE) foo.pr --check

test-ada: 
	$(OPENGEODE) *.pr --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn
	gnat make test_ada.ada
	./test_ada | diff expected -

test-c: 
	$(OPENGEODE) *.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn 
	$(CC) -O$(O) -o test_c *.c
	./test_c | diff expected -

coverage:
	coverage run -p $(OPENGEODE) *.pr --toAda

.PHONY: all edit test-parse test-ada test-c coverage
