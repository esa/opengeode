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
	gnatlink test_ada.o operators.ali -lgnat -lm -o testcase
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py operators.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc operators.ll
	clang -c operators.s
	clang -c dataview-uniq.c
	clang -c test_llvm.c
	clang operators.o dataview-uniq.o test_llvm.o -o testcase -lm
	./testcase | diff expected -

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h
