include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

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

test-c: og.c test_c.o dataview-uniq.o
	$(CC) og.c -c -o og.o
	$(CC) test_c.o og.c dataview-uniq.o -lm -o test_c
	./test_c

test-rust:
	$(OPENGEODE) og.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s/$$/\nuse crate::dataview_uniq::*;/' "$$f"; \
	  fi; \
	done && \
	sed -i '/^pub const /d' dataview-uniq.rs && \
	sed -i 's/use crate::dataview_uniqDef/use super::dataview_uniqDef/g; s/use crate::dataview_uniq/use super::dataview_uniq/g; s/use crate::og_type_datamodelDef/use super::og_type_datamodelDef/g' og_type_datamodel.rs og_type_datamodelDef.rs dataview-uniq.rs 2>/dev/null; \
	sed -i 's/fn ri_0_rezult[^}]*/fn ri_0_rezult(_res: \&mut asn1SccMy_OctStr) { print!("[C] got something]\\n"); /' og_type.rs 2>/dev/null || true && \
	cp og_cargo.toml Cargo.toml && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected -

test-if:
	sdl2if og.pr system_structure.pr


test-llvm: og.o dataview-uniq.o | test_llvm.o
	$(CC) og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm


coverage:
	coverage run -p $(OPENGEODE) og.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-rust test-llvm coverage

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
