include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) challenge.pr system_structure.pr

test-parse:
	$(OPENGEODE) challenge.pr system_structure.pr --check

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
	cp challenge_ri.ada challenge_ri.adb
	$(OPENGEODE) challenge.pr system_structure.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make challenge
	$(GNATBIND) -n challenge.ali
	$(GNATLINK) -o test_ada  test_ada.o challenge.ali -lm
	./test_ada | diff expected -

test-c: challenge.c test_c.o dataview-uniq.o
	$(CC) -include missing.h challenge.c -c -o challenge.o
	$(CC) test_c.o challenge.c dataview-uniq.o -lm -o test_c
	./test_c | diff expected -

test-if:
	sdl2if challenge.pr system_structure.pr

test-llvm: challenge.o dataview-uniq.o | test_llvm.o
	$(CC) challenge.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm| diff expected -

test-rust:
	$(OPENGEODE) challenge.pr system_structure.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate::.*Def/a use crate::dataview_uniq::*;' "$$f"; \
	  fi; \
	done && \
	cp challenge_cargo.toml Cargo.toml && \
	cargo build 2>&1
	# RUST_COMPILE_ONLY: compile verification only (generated Rust needs more fixes before it can run)

coverage:
	coverage run -p $(OPENGEODE) challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage test-rust

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
