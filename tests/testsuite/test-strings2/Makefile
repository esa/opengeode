include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

test-ada: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -gnat2022 -O$(O) -c *.adb
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o og.ali
	./test_ada | diff - expected

test-c: dataview-uniq.o | test_ada.o
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) test_c.c og.c dataview-uniq.c -o test_c
	./test_c | diff - expected

test-if:
	sdl2if og.pr


coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

test-rust:
	$(OPENGEODE) og.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s|$$|\nuse crate::dataview_uniq::*;\nuse crate::dataview_uniqDef::*;|' "$$f"; \
	  fi; \
	done && \
	cp og_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -
.PHONY: all edit test-parse test-ada test-rust coverage
