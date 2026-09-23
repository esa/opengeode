include ../shared.mk

ROOT_MODEL=og.pr

all: test-ada

edit:
	$(OPENGEODE) og.pr

test-parse:
	$(OPENGEODE) og.pr --check

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
	$(OPENGEODE) og.pr --toAda
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	gnat make og -g
	$(GNATBIND) -n og.ali
	$(GNATLINK) -o test_ada  test_ada.o og.ali -lm
	./test_ada | diff expected.log -

test-if:
	sdl2if og.pr

test-c:
	$(OPENGEODE) og.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -equal *.asn
	$(CC) -O$(O) -c -g test_c.c
	$(CC) og.c -c -o og.o
	$(CC) dataview-uniq.c -c -o dataview-uniq.o
	$(CC) og_datamodel.c -c -o og_datamodel.o
	$(CC) test_c.o og.c dataview-uniq.o og_datamodel.o -lm -o test_c
	./test_c | diff expected.log -

test-python:
	$(OPENGEODE) og.pr --shared
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(GNATMAKE) -O$(O) -gnat2012 -fPIC -c *.adb
	$(GNATBIND) -n -Llibog og
	$(GNATMAKE) -c -fPIC -gnat2012 b~og.adb
	$(CC) -shared -fPIC -o libog.so b~og.o og.o adaasn1rtl.o taste_dataview.o
	python -c "from ctypes import *; test=CDLL('./libog.so'); test.liboginit(); test.og_for_a(); test.og_for_b(); test.og_for_a(); test.og_for_b()"


test-rust:
	$(OPENGEODE) og.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn && \
	for f in *_datamodel.rs; do \
	  if [ -f "$$f" ] && ! grep -q 'use crate::dataview_uniq::' "$$f"; then \
	    sed -i '/^use crate.*Def/s/$$/\nuse crate::dataview_uniq::*;/' "$$f"; \
	  fi; \
	done && \
	cp og_cargo.toml Cargo.toml && \
	printf '%s\n' '#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,' \
		'unused_variables, unused_mut, unused_assignments, dead_code)]' \
		'use og::*;' \
		'use og::dataview_uniqDef::*;' \
		'fn main() {' \
		'    unsafe {' \
		'        og_startup();' \
		'        for_a();' \
		'        for_a();' \
		'        for_a();' \
		'        for_b();' \
		'        for_b();' \
		'        let mut param: asn1SccMyInteger = 1;' \
		'        reset_all(&mut param);' \
		'        reset_all(&mut param);' \
		'        exit_aggreg();' \
		'    }' \
		'}' > main.rs && \
	cargo build 2>&1 && \
	./target/debug/test_rust | diff expected.log -

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

.PHONY: all edit test-parse test-ada test-rust coverage

# Override shared.mk clean to preserve main.rs (hand-authored harness)
clean:
	-mv main.rs main.rs.bak 2>/dev/null
	gnat clean *.adb
	rm -rf *.if *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn GPS_project.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_c \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check obj src code *_datamodel.asn asn1_x86.gpr *_ada.gpr *.pml x86 \
		   *.dump *.rs *_cargo.toml *_datamodelDef.rs *_datamodel.rs asn1rust/ \
		   Cargo.toml target
	-mv main.rs.bak main.rs 2>/dev/null
