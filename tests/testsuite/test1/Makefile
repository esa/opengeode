include ../shared.mk

ROOT_MODEL=system_structure.pr

edit:
	$(OPENGEODE) og.pr system_structure.pr

test-parse:
	$(OPENGEODE) og.pr system_structure.pr --check

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

test-ada: og.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada test_ada.o dataview-uniq.o og.ali
	./test_ada
	#gcov og.adb

test-if: og.if

test-c: og.c test_c.o dataview-uniq.o
	$(CC) og.c -c -o og.o
	$(CC) test_c.o og.c dataview-uniq.o -lm -o test_c
	./test_c

test-if:
	sdl2if og.pr system_structure.pr


test-llvm: og.o dataview-uniq.o | test_llvm.o
	$(CC) og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm


test-rust:
	$(OPENGEODE) og.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	sed -i '/^pub const /d' dataview-uniq.rs && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate::.*Def/a use crate::dataview_uniq::*;' "$$f"; \
	  fi; \
	done && \
	cp og_cargo.toml Cargo.toml && \
	python3 patch_ri.py og.rs && \
	printf '%s\n' '#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,' \
		'unused_variables, unused_mut, unused_assignments, dead_code)]' \
		'use og::*;' \
		'use og::dataview_uniqDef::*;' \
		'fn main() {' \
		'    unsafe {' \
		'        og_startup();' \
		'        let mut toto = test_string;' \
		'        go(&mut toto);' \
		'        go(&mut toto);' \
		'        go(&mut toto);' \
		'    }' \
		'}' > main.rs && \
	cargo build 2>&1
	# RUST_COMPILE_ONLY: compile verification only (generated Rust needs more fixes before it can run)

coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: edit test-parse test-qgen-parse test-ada test-llvm coverage test-rust
