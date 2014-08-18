include ../shared.mk

all: test-ada test-llvm

edit:
	../../../opengeode.py myfunction.pr system_structure.pr

test-parse:
	../../../opengeode.py myfunction.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda myfunction.pr system_structure.pr || exit 1
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c myfunction.adb
	gcc -c test_ada.c
	gnatbind -n myfunction.ali
	gnatlink -o test_ada test_ada.o myfunction.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	../../../opengeode.py myfunction.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc myfunction.ll
	gcc -c myfunction.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc myfunction.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run  -p ../../../opengeode.py myfunction.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: all edit test-parse test-ada test-llvm coverage clean