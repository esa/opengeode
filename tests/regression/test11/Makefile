all: test-ada test-llvm

test-parse:
	../../../opengeode.py og.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda og.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n og.ali
	gnatlink -o testcase test_ada.o og.ali -lgnat
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py og.pr system_structure.pr --llvm
	llc og.ll
	gcc -c og.s
	gcc -c test_llvm.c
	gcc og.o test_llvm.o -o testcase
	# loops forever. Fail until fixed
	#./testcase | diff expected -
	exit 1


coverage:
	coverage run -p ../../../opengeode.py og.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s
