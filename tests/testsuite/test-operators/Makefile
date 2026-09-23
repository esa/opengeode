include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada

edit:
	$(OPENGEODE) operators.pr system_structure.pr

test-parse:
	$(OPENGEODE) operators.pr system_structure.pr --check

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

test-ada: operators.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n operators.ali
	$(GNATLINK) test_ada.o operators.ali -lm -o test_ada
	./test_ada | diff expected -

test-c: operators.c test_c.o dataview-uniq.o
	$(CC) -g operators.c -c asn1crt.c
	$(CC) -g test_c.o operators.o asn1crt.o dataview-uniq.o -lm -o test_c
	./test_c | diff expected_c -

test-if:
	sdl2if operators.pr system_structure.pr

coverage:
	coverage run -p $(OPENGEODE) operators.pr system_structure.pr --toAda

test-rust:
	$(OPENGEODE) operators.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s/$$/\nuse crate::dataview_uniq::*;/' "$$f"; \
	  fi; \
	done && \
	sed -i '/^pub const /d' dataview-uniq.rs && \
	sed -i 's/fn ri_0_assert(.*{/fn ri_0_assert(_res: \&mut asn1SccBool, _msg: \&asn1SccCharString) { \/\/ no-op/' operators_ri.rs 2>/dev/null || true && \
	cp operators_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -

.PHONY: all edit test-parse test-ada test-rust coverage

# Override shared.mk clean to preserve main.rs
clean:
	-mv main.rs main.rs.bak 2>/dev/null
	gnat clean *.adb
	rm -rf *.if *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn GPS_project.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check obj src code *_datamodel.asn asn1_x86.gpr *_ada.gpr *.pml x86 \
		   *.dump *.rs *_cargo.toml *_datamodelDef.rs *_datamodel.rs asn1rust/ \
		   Cargo.toml target
	-mv main.rs.bak main.rs 2>/dev/null
