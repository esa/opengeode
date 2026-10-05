include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) --check orchestrator.pr system_structure.pr

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

test-ada: dataview-uniq.o | test_ada.o
	cp orchestrator_ri.ada orchestrator_ri.adb
	cp test_ada.ada test_ada.adb
	$(OPENGEODE) orchestrator.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn
	gnat make -g test_ada
	./test_ada | diff expected -

test-c: orchestrator.c test_c.o dataview-uniq.o
	$(CC) orchestrator.c asn1crt.c -c 
	$(CC) test_c.o orchestrator.o asn1crt.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected_c -

test-if:
	sdl2if orchestrator.pr sytem_structure.pr

test-rust:
	$(OPENGEODE) orchestrator.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s|$$|\nuse crate::dataview_uniq::*;\nuse crate::dataview_uniqDef::*;|' "$$f"; \
	  fi; \
	done && \
	cp orchestrator_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -
coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada coverage test-rust
