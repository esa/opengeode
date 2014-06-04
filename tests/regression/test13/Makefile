all: compile

generate-ada:
	../../../opengeode.py math.pr system_structure.pr --check --toAda

compile-ada: generate-ada
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c	test.c
	gnatbind -n math.ali
	gnatlink -o testcase  test.o math.ali -lgnat -lm
	./testcase && echo 'All OK!'

generate-llvm:
	../../../opengeode.py math.pr system_structure.pr --check --llvm

parse:
	../../../opengeode.py math.pr system_structure.pr --check

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr testcase
