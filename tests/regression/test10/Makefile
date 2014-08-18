include ../shared.mk

all: test-ada test-llvm

edit:
	../../../opengeode.py challenge.pr system_structure.pr

test-parse:
	../../../opengeode.py challenge.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda challenge.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c	test_ada.c
	gnatbind -n challenge.ali
	gnatlink -o test_ada  test_ada.o challenge.ali -lgnat -lm
	./test_ada | diff expected -

test-llvm:
	../../../opengeode.py challenge.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc challenge.ll
	gcc -c challenge.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc challenge.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm| diff expected -

coverage:
	coverage run -p ../../../opengeode.py challenge.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage