include ../shared.mk

ROOT_MODEL=toto.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) toto.pr

test-parse:
	$(OPENGEODE) toto.pr --check

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

test-ada: 
	mkdir -p src && cd src && $(OPENGEODE) ../toto.pr -g --toAda && \
	cp ../test_toto.ada test_toto.adb && \
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal ../*.asn *.asn
	mkdir -p obj && cd obj && gnat make -O$(O) ../src/test_toto && \
	./test_toto | diff ../expected -

test-c: 
	$(OPENGEODE) toto.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -renamePolicy 3 -equal -fp AUTO *.asn 
	$(CC) -O$(O) -o test_c *.c
	./test_c | diff expected -
	
test-if:
	sdl2if toto.pr


test-llvm:
	$(OPENGEODE) toto.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


coverage:
	coverage run -p $(OPENGEODE) toto.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
