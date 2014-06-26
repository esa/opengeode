all: test

parse:
	../../../opengeode.py sequences.pr system_structure.pr --check

generate-ada:
	@../../../opengeode.py sequences.pr system_structure.pr --check --toAda

compile-ada: generate-ada
	@asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	@gnatmake -c *.adb

run-ada: compile-ada
	@gcc -c test_ada.c
	@gnatbind -n sequences.ali
	@gnatlink test_ada.o sequences.ali -lgnat -lm -o testcase
	@./testcase | diff expected -

generate-llvm:
	@../../../opengeode.py sequences.pr system_structure.pr --check --llvm

compile-llvm: generate-llvm
	@llc sequences.ll
	@gcc -c sequences.s

run-llvm: compile-llvm
	@gcc -c test_llvm.c
	@gcc sequences.o test_llvm.o -o testcase
	@./testcase | diff expected -

test: run-ada run-llvm
	echo "ALL OK!"

clean:
	@rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr testcase
