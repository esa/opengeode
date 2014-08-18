all: test-ada test-llvm

edit:
	../../../opengeode.py fce.pr system_structure.pr

test-parse:
	../../../opengeode.py fce.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda fce.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c fce.adb

test-llvm:
	../../../opengeode.py fce.pr system_structure.pr --llvm
	llc fce.ll
	gcc -c fce.s

coverage:
	coverage run -p ../../../opengeode.py fce.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s

.PHONY: all edit test-parse test-ada test-llvm coverage clean