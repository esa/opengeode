all: test-ada test-llvm

edit:
	../../../opengeode.py trafficlight.pr system_structure.pr

test-parse:
	../../../opengeode.py trafficlight.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda trafficlight.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	#gcc -c test.c
	#gnatbind -n trafficlight.ali
	#gnatlink -o testcase test.o trafficlight.ali -lgnat -lm

test-llvm:
	../../../opengeode.py trafficlight.pr system_structure.pr --llvm
	llc trafficlight.ll
	gcc -c trafficlight.s

test-export:
	../../../opengeode.py --png --pdf --svg trafficlight.pr system_structure.pr
	../../../opengeode.py --png --pdf --svg --split trafficlight.pr system_structure.pr

coverage:
	coverage run -p ../../../opengeode.py trafficlight.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr testcase *.ll *.s *.pdf *.svg *.png

.PHONY: all edit test-parse test-ada test-llvm test-exports coverage clean