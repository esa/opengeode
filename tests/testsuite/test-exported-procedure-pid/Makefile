include ../shared.mk

ROOT_MODEL=system_structure.pr

all: test-c

edit:
	$(OPENGEODE) child_type.pr $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) child_type.pr $(ROOT_MODEL) --check

# Regression test: an exported procedure of a process TYPE with a PID type in
# the dataview must compile. Its automatic <type>_<name>_transition call used
# to pass a destination PID to a function declared without one.
test-c:
	$(OPENGEODE) child_type.pr $(ROOT_MODEL) --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -o test_c test_c.c child.c child_type_datamodel.c \
	    dataview-uniq.c asn1crt.c && ./test_c | diff expected -

# The same model must generate cleanly in Ada and Rust.
test-ada:
	$(OPENGEODE) child_type.pr $(ROOT_MODEL) --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn

test-rust:
	$(OPENGEODE) child_type.pr $(ROOT_MODEL) --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) child_type.pr $(ROOT_MODEL) --toC

.PHONY: all edit test-parse test-c test-ada test-rust coverage

clean:
	rm -rf *.adb *.ads *.pyc *.o *.ali asn1_x86.gpr *_ada.gpr \
	       dataview-uniq.c dataview-uniq.h test_c test_ada \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h \
	       *_datamodel.asn *_datamodel.c *_datamodel.h *.rs *_cargo.toml \
	       *_datamodelDef.rs *_datamodel.rs asn1rust/ Cargo.toml Cargo.lock target
