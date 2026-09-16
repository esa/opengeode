include ../shared.mk

ROOT_MODEL=decision.pr

all: test-ada test-c

edit:
	$(OPENGEODE) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) $(ROOT_MODEL) --check

test-ada:
	$(OPENGEODE) --toAda --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn
	$(GNATMAKE) -O$(O) -c *.adb
	$(GNATBIND) -n complexsdl.ali

test-c: 
	$(OPENGEODE) --toC --dumpAST $(ROOT_MODEL)
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO  *.asn
	$(CC) -O$(O) -c *.c

test-rust:
	$(OPENGEODE) --toRust $(ROOT_MODEL) && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) og.pr --toAda

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
