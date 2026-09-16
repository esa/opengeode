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
	    sed -i '/^use crate::.*Def/a use crate::dataview_uniq::*;' "$$f"; \
	  fi; \
	done && \
	cp expressions_cargo.toml Cargo.toml && \
	sed -i 's|fn ri_0_assert(res: &mut asn1SccBoolean, msg: &mut asn1SccCharString) { /\* RI stub \*/ }|fn ri_0_assert(res: \&mut asn1SccBoolean, msg: \&mut asn1SccCharString) { let mut end = 0; while end < msg.arr.len() \&\& msg.arr[end] != 0 { end += 1; } let s = std::str::from_utf8(\&msg.arr[..end]).unwrap_or(""); if *res { println!("PASS: {}", s); } else { println!("FAIL: {}", s); } }|' expressions.rs && \
	cargo build 2>&1
	# RUST_COMPILE_ONLY: generated Rust needs array padding fixes before it can compile

.PHONY: all edit test-parse test-ada test-llvm test-rust coverage
