all: test-ada

edit:
	../../../opengeode.py og.pr system_structure.pr

test-parse:
	../../../opengeode.py og.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda og.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c og.adb

coverage:
	coverage run -p ../../../opengeode.py og.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr
