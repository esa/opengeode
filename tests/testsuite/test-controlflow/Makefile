include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) controlflow.pr system_structure.pr

test-parse:
	$(OPENGEODE) controlflow.pr system_structure.pr --check

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

test-ada: controlflow.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n controlflow.ali
	$(GNATLINK) test_ada.o controlflow.ali -o test_ada
	./test_ada | diff expected -

test-c: controlflow.c test_c.o dataview-uniq.o
	$(CC) -c asn1crt.c controlflow.c dataview-uniq.c
	$(CC) test_c.o asn1crt.o controlflow.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected -

test-if:
	sdl2if controlflow.pr system_structure.pr

test-llvm: controlflow.o dataview-uniq.o | test_llvm.o
	$(CC) controlflow.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

test-vhdl : test-c
	bambu controlflow.c test_c.c --experimental-setup=BAMBU --debug-classes=MuxConnectionBinding --print-dot --no-clean --pretty-print=a.c -d2

test-rust:
	$(OPENGEODE) controlflow.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s/$$/\nuse crate::dataview_uniq::*;/' "$$f"; \
	  fi; \
	done && \
	cp controlflow_cargo.toml Cargo.toml && \
	python3 patch_ri.py controlflow.rs && \
	printf '%s\n' '#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,' \
		'unused_variables, unused_mut, unused_assignments, dead_code)]' \
		'use controlflow::*;' \
		'use controlflow::dataview_uniqDef::*;' \
		'fn main() {' \
		'    unsafe {' \
		'        controlflow_startup();' \
		'        run();' \
		'    }' \
		'}' > main.rs && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -

coverage:
	coverage run -p $(OPENGEODE) controlflow.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm test-rust coverage

# Override shared.mk clean to preserve main.rs
clean:
	-mv main.rs main.rs.bak 2>/dev/null
	gnat clean *.adb
	rm -rf *.if *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn GPS_project.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check obj src code *_datamodel.asn asn1_x86.gpr *_ada.gpr *.pml x86 \
		   *.dump *.rs *_cargo.toml *_datamodelDef.rs *_datamodel.rs asn1rust/ \
		   Cargo.toml target
	-mv main.rs.bak main.rs 2>/dev/null
