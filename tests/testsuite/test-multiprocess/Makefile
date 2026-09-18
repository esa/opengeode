include ../shared.mk

ROOT_MODEL=toto.pr

all: test-ada test-llvm

edit:
	$(OPENGEODE) toto.pr

test-parse:
	$(OPENGEODE) toto.pr --check 2<&1 || exit 0

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

test-c: 
	
test-if:
	sdl2if toto.pr


test-llvm:
	$(OPENGEODE) toto.pr --llvm -O$(O)
	$(LLC) *.ll
	$(CC) -O$(O) -c *.s


test-rust:
	@:

coverage:
	coverage run -p $(OPENGEODE) toto.pr --toAda

.PHONY: all edit test-parse test-ada test-rust test-llvm coverage
