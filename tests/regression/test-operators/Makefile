include ../shared.mk

all: test-ada

edit:
	../../../opengeode.py operators.pr system_structure.pr

test-parse:
	../../../opengeode.py operators.pr system_structure.pr --check

test-ada:
	../../../opengeode.py operators.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n operators.ali
	gnatlink test_ada.o operators.ali -lgnat -lm -o test_ada
	./test_ada | diff expected -

test-llvm:
	../../../opengeode.py operators.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc operators.ll
	clang -c operators.s
	clang -c dataview-uniq.c
	clang -c test_llvm.c
	clang operators.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

.PHONY: all edit test-parse test-ada test-llvm