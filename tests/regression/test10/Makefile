all: test-ada

edit:
	../../../opengeode.py challenge.pr system_structure.pr

test-parse:
	../../../opengeode.py challenge.pr system_structure.pr --check

test-ada:
	../../../opengeode.py --toAda challenge.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c	test.c
	gnatbind -n challenge.ali
	gnatlink -o testcase  test.o challenge.ali -lgnat -lm
	./testcase | diff expected -

coverage:
	coverage run -p ../../../opengeode.py challenge.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr testcase
