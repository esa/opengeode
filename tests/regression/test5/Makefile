all: test-ada

test-parse:
	../../../opengeode.py function0.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda function0.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c function0.adb

coverage:
	coverage run -p ../../../opengeode.py function0.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr
