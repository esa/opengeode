include ../shared.mk

all: test-ada test-llvm

edit:
	../../../opengeode.py og.pr system_structure.pr

test-parse:
	../../../opengeode.py og.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda og.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n og.ali
	gnatlink -o test_ada test_ada.o og.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	../../../opengeode.py og.pr system_structure.pr --llvm
	asn1.exe -c dataview-uniq.asn -equal -typePrefix asn1Scc
	llc og.ll
	gcc -c og.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc og.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p ../../../opengeode.py og.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: all edit test-parse test-ada test-llvm coverage clean