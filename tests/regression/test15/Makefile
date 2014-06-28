all: test-ada test-llvm

test-parse:
	../../../opengeode.py controlflow.pr system_structure.pr --check

test-ada:
	../../../opengeode.py controlflow.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n controlflow.ali
	gnatlink test_ada.o controlflow.ali -lgnat -lm -o testcase
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py controlflow.pr system_structure.pr --check --llvm
	llc controlflow.ll
	gcc -c controlflow.s
	gcc -c test_llvm.c
	gcc controlflow.o test_llvm.o -o testcase
	./testcase | diff expected -

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s
