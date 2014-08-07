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
	gnatlink test_ada.o expressions.ali -lgnat -lm -o testcase
	./testcase

test-llvm:
	../../../opengeode.py expressions.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc expressions.ll
	clang -c expressions.s
	clang -c dataview-uniq.c
	clang -c test_llvm.c
	clang expressions.o dataview-uniq.o test_llvm.o -o testcase
	./testcase

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h
