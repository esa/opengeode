all: test-ada test-llvm

edit:
	../../../opengeode.py challenge.pr system_structure.pr

test-parse:
	../../../opengeode.py challenge.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda challenge.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c challenge.adb

test-llvm:
	../../../opengeode.py challenge.pr system_structure.pr --llvm
	llc challenge.ll
	gcc -c challenge.s

coverage:
	coverage run -p ../../../opengeode.py challenge.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s
