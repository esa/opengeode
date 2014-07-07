all: test-ada test-llvm

test-parse:
	../../../opengeode.py sequences.pr system_structure.pr --check

test-ada:
	../../../opengeode.py sequences.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n sequences.ali
	gnatlink test_ada.o sequences.ali -lgnat -lm -o testcase
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py sequences.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -equal
	llc sequences.ll
	clang -c sequences.s
	clang -c dataview-uniq.c
	clang -c test_llvm.c
	clang sequences.o dataview-uniq.o test_llvm.o -o testcase
	./testcase | diff expected -

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s
