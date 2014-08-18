include ../shared.mk

all: test-ada

edit:
	../../../opengeode.py expressions.pr system_structure.pr

test-parse:
	../../../opengeode.py expressions.pr system_structure.pr --check

test-ada:
	../../../opengeode.py expressions.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n expressions.ali
	gnatlink test_ada.o expressions.ali -lgnat -lm -o test_ada
	./test_ada

test-llvm:
	../../../opengeode.py expressions.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc expressions.ll
	gcc -c expressions.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc expressions.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: all edit test-parse test-ada test-llvm clean