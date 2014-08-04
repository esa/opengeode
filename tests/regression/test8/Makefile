all: test-ada

edit:
	../../../opengeode.py orchestrator.pr system_structure.pr

test-parse:
	../../../opengeode.py --check orchestrator.pr system_structure.pr

test-ada:
	../../../opengeode.py --toAda orchestrator.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c *.adb
	gcc -c test.c
	gnatbind -n orchestrator.ali
	gnatlink -o testcase test.o orchestrator.ali -lgnat
	./testcase | diff expected -

coverage:
	coverage run -p ../../../opengeode.py orchestrator.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr datav*.? ber.c xer.c asn1crt.? acn.c real.c testcase
