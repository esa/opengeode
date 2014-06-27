all: test-ada

test-parse:
	../../../opengeode.py myfunction.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda myfunction.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c myfunction.adb

coverage:
	coverage run  -p ../../../opengeode.py myfunction.pr system_structure.pr --toAda


clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr
