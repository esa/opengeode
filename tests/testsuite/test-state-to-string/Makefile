include ../shared.mk

ROOT_MODEL=decision.pr

all: test-ada test-c test-rust

edit:
	$(OPENGEODE) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) $(ROOT_MODEL) --check

test-ada:
	$(OPENGEODE) decision.pr --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -o test_ada test_ada.ada && ./test_ada | diff expected -

test-c:
	$(OPENGEODE) decision.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -o test_c test_c.c complexsdl.c complexsdl_datamodel.c \
	    dataview-uniq.c asn1crt.c && ./test_c | diff expected -

# Rust <proc>_state() returns the same NUL-terminated string as Ada and C.
test-rust:
	$(OPENGEODE) decision.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s|$$|\nuse crate::dataview_uniq::*;\nuse crate::dataview_uniqDef::*;|' "$$f"; \
	  fi; \
	done && \
	cp complexsdl_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -

coverage:
	coverage run -p $(OPENGEODE) $(ROOT_MODEL) --toAda

.PHONY: all edit test-parse test-ada test-c test-rust coverage
