all: test-ada test-llvm

test-parse:
	../../../opengeode.py basic.pr system_structure.pr --check

test-ada:
	../../../opengeode.py basic.pr system_structure.pr --check --toAda
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n basic.ali
	gnatlink test_ada.o basic.ali -lgnat -lm -o testcase
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py basic.pr system_structure.pr --check --llvm
	llc basic.ll
	gcc -c basic.s
	gcc -c test_llvm.c
	gcc basic.o test_llvm.o -o testcase
	./testcase | diff expected -

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s
