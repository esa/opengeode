include ../shared.mk

ROOT_MODEL=cd.pr

all: test-c

edit:
	$(OPENGEODE) $(ROOT_MODEL)

test-parse:
	$(OPENGEODE) $(ROOT_MODEL) --check

# CREATE and STOP are supported end-to-end in the C backend; the runtime test
# exercises them with the environment glue (create/delete instance) provided
# locally in glue.c.
test-c:
	$(OPENGEODE) cd.pr --toC
	$(ASN1SCC) -c -ig -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn
	$(CC) -O$(O) -o test_c test_c.c parent.c parent_datamodel.c \
	    dataview-uniq.c asn1crt.c && ./test_c | diff expected -

# The Ada and Rust backends also emit CREATE/STOP code; only generation is
# checked here (their runtime glue for standalone processes is TASTE-provided).
test-ada:
	$(OPENGEODE) cd.pr --toAda
	$(ASN1SCC) -Ada -adaBitStringAlignment -typePrefix asn1Scc -equal *.asn

test-rust:
	$(OPENGEODE) cd.pr --toRust && \
	$(ASN1SCC) -Rust -typePrefix asn1Scc -renamePolicy 3 -equal *.asn

coverage:
	coverage run -p $(OPENGEODE) $(ROOT_MODEL) --toC

.PHONY: all edit test-parse test-c test-ada test-rust coverage

clean:
	rm -rf *.adb *.ads *.pyc *.o *.ali asn1_x86.gpr *_ada.gpr \
	       dataview-uniq.c dataview-uniq.h test_c test_ada \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h \
	       *_datamodel.asn *_datamodel.c *_datamodel.h *.rs *_cargo.toml \
	       *_datamodelDef.rs *_datamodel.rs asn1rust/ Cargo.toml Cargo.lock target
