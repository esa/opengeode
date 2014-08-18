all: test-ada

edit:
	../../../opengeode.py myfunction.pr system_structure.pr

check:
	../../../opengeode.py myfunction.pr system_structure.pr --check

test-parse:
	../../../opengeode.py myfunction.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda myfunction.pr system_structure.pr 2>&1 | sort | diff expected - || exit 0

coverage:
	coverage run  -p ../../../opengeode.py myfunction.pr system_structure.pr --toAda


clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr datav*.? ber.c xer.c asn1crt.? acn.c real.c testcase

.PHONY: all edit check test-parse test-ada coverage clean