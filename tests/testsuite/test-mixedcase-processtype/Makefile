include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-c

edit:
	$(OPENGEODE) MixedType.pr $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) MixedType.pr $(ROOT_MODEL) --check

# Regression test: a mixed-case process TYPE, instantiated. The generated
# instance wrapper must call the type module's symbols with the casing the
# type module emits them with (lowercased function names). It used to use the
# type name verbatim, so the generated C did not compile.
test-c:
	$(OPENGEODE) MixedType.pr $(ROOT_MODEL) --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -o test_c test_c.c glue.c child.c mixedtype_datamodel.c \
	    dataview-uniq.c asn1crt.c && ./test_c | diff expected -

# The same model must generate cleanly in Ada and Rust.
test-ada:
	$(OPENGEODE) MixedType.pr $(ROOT_MODEL) --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn

test-rust:
	$(OPENGEODE) MixedType.pr $(ROOT_MODEL) --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) MixedType.pr $(ROOT_MODEL) --toC

.PHONY: all edit test-parse test-c test-ada test-rust coverage

clean:
	rm -rf *.adb *.ads *.pyc *.o *.ali asn1_x86.gpr *_ada.gpr \
	       dataview-uniq.c dataview-uniq.h test_c test_ada \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h \
	       *_datamodel.asn *_datamodel.c *_datamodel.h *.rs *_cargo.toml \
	       *_datamodelDef.rs *_datamodel.rs asn1rust/ Cargo.toml Cargo.lock target
