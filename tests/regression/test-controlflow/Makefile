all: test-ada

edit:
	../../../opengeode.py controlflow.pr system_structure.pr

test-parse:
	../../../opengeode.py controlflow.pr system_structure.pr --check

test-ada:
	../../../opengeode.py controlflow.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n controlflow.ali
	gnatlink test_ada.o controlflow.ali -lgnat -lm -o testcase
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py controlflow.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc controlflow.ll
	gcc -c controlflow.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc controlflow.o dataview-uniq.o test_llvm.o -o testcase
	./testcase | diff expected -

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h

.PHONY: all edit test-parse test-ada test-llvm clean