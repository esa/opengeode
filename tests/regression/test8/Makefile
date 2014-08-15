all: test-ada test-llvm

edit:
	../../../opengeode.py orchestrator.pr system_structure.pr

test-parse:
	../../../opengeode.py --check orchestrator.pr system_structure.pr

test-ada:
	../../../opengeode.py --toAda orchestrator.pr system_structure.pr
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc
	gnatmake -c *.adb
	gcc -c test_ada.c
	gnatbind -n orchestrator.ali
	gnatlink -o testcase test_ada.o orchestrator.ali -lgnat
	./testcase | diff expected -

test-llvm:
	../../../opengeode.py orchestrator.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc orchestrator.ll
	gcc -c orchestrator.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc orchestrator.o dataview-uniq.o test_llvm.o -o testcase -lm
	./testcase | diff expected -

coverage:
	coverage run -p ../../../opengeode.py orchestrator.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr datav*.? ber.c xer.c asn1crt.? acn.c real.c *.wrn *.gpr testcase *.ll *.s
