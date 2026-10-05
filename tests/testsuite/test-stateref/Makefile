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

# Override shared.mk clean to preserve main.rs
clean:
	-mv main.rs main.rs.bak 2>/dev/null
	gnat clean *.adb
	rm -rf *.if *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn GPS_project.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_c \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check obj src code *_datamodel.asn asn1_x86.gpr *_ada.gpr *.pml x86 \
	       *.dump *.rs *_cargo.toml *_datamodelDef.rs *_datamodel.rs asn1rust/ \
	       Cargo.toml Cargo.lock target
	-mv main.rs.bak main.rs 2>/dev/null
