include ../shared.mk

ROOT_MODEL=*.pr

all: test-ada

edit:
	$(OPENGEODE) *.pr

test-parse:
	$(OPENGEODE) *.pr --check

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
	$(MAKE) -f Makefile.renaming
	cp test.ada code && cd code && gnat make test.ada && ./test | diff ../expected - || exit 1

test-c:
	$(OPENGEODE) *.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) *.c -o test_c && ./test_c | diff expected -

test-rust:
	$(OPENGEODE) *.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s|$$|\nuse crate::dataview_uniq::*;\nuse crate::dataview_uniqDef::*;|' "$$f"; \
	  fi; \
	done && \
	cp renaming_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -
test-if:
	sdl2if *.pr


coverage:
	coverage run -p $(OPENGEODE) *.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage
