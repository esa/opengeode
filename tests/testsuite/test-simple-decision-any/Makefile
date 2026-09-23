include ../shared.mk

ROOT_MODEL=decision_any.pr

all: test-ada test-c

edit:
	$(OPENGEODE) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) $(ROOT_MODEL) --check

test-ada:
	echo 'package Shared_Counts is' > shared_counts.ads
	echo '   type Count_Array is array (1 .. 4) of Integer;' >> shared_counts.ads
	echo '   Counts : Count_Array := (others => 0);' >> shared_counts.ads
	echo 'end Shared_Counts;' >> shared_counts.ads
	$(OPENGEODE) --toAda --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	cp -f complexsdl_ri.ada complexsdl_ri.adb
	cp -f shared_counts.ada shared_counts.ads
	$(GNATMAKE) -O$(O) -o test_ada test_ada.ada
	./test_ada

test-c:
	$(OPENGEODE) --toC --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -g -o test_c complexsdl.c test_c.c dataview-uniq.c
	./test_c

test-rust:
	$(OPENGEODE) --toRust $(ROOT_MODEL) && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada coverage test-rust
