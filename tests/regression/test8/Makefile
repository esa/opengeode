include ../shared.mk

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
	gnatlink -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada | diff expected -

test-llvm:
	../../../opengeode.py orchestrator.pr system_structure.pr --check --llvm
	asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
	llc orchestrator.ll
	gcc -c orchestrator.s
	gcc -c dataview-uniq.c
	gcc -c test_llvm.c
	gcc orchestrator.o dataview-uniq.o test_llvm.o -o test_llvm -lm
	./test_llvm | diff expected -

coverage:
	coverage run -p ../../../opengeode.py orchestrator.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner \
	bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h real.c xer.c \
	ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: all edit test-parse test-ada test-llvm coverage clean