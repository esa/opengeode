all: compile

generate-ada:
	../../../opengeode.py adder.pr system_structure.pr --check --toAda

compile-ada: generate-ada
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c	test.c
	gnatbind -n adder.ali
	gnatlink -o testcase  test.o adder.ali -lgnat -lm
	./testcase | diff expected - && echo 'All OK!'

generate-llvm:
	../../../opengeode.py adder.pr system_structure.pr --check --llvm

parse:
	../../../opengeode.py adder.pr system_structure.pr --check

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr testcase
