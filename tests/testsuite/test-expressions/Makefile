include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) expressions.pr system_structure.pr

test-parse:
	$(OPENGEODE) expressions.pr system_structure.pr --check

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

test-ada: clean
	$(MAKE) test_ada.adb
	$(MAKE) expressions.adb
	gnat make test_ada -O$(O) -g -ffunction-sections -fdata-sections -Wl,-gc-sections
	./test_ada | diff expected -

expressions.adb: expressions.pr expressions_ri.adb
	$(OPENGEODE) expressions.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn

test_ada.adb: test_ada.ada
	cp test_ada.ada test_ada.adb

expressions_ri.adb: expressions_ri.ada
	cp expressions_ri.ada expressions_ri.adb

test-c: expressions.c test_c.o dataview-uniq.o
	$(CC) expressions.c -c asn1crt.c
	$(CC) test_c.o dataview-uniq.o asn1crt.o expressions.o -lm -o test_c
	./test_c | diff expected_c -
	
test-if:
	sdl2if expressions.pr system_structure.pr

test-llvm: expressions.o dataview-uniq.o | test_llvm.o
	$(CC) expressions.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

test-vhdl : test-c
	bambu expressions.c test_c.c dataview-uniq.c --experimental-setup=BAMBU -v4

coverage:
	coverage run -p $(OPENGEODE) expressions.pr system_structure.pr --toAda

test-rust:
	$(OPENGEODE) expressions.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s/$$/\nuse crate::dataview_uniq::*;/' "$$f"; \
	  fi; \
	done && \
	cp expressions_cargo.toml Cargo.toml && \
	python3 patch_ri.py expressions.rs && \
	printf '%s\n' '#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,' \
		'unused_variables, unused_mut, unused_assignments, dead_code)]' \
		'use expressions::*;' \
		'use expressions::dataview_uniqDef::*;' \
		'fn main() {' \
		'    unsafe {' \
		'        expressions_startup();' \
		'        run();' \
		'    }' \
		'}' > main.rs && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -

.PHONY: all edit test-parse test-ada test-llvm test-rust coverage
