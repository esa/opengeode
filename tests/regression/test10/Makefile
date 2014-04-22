all: compile

generate-code:
	../../../opengeode.py --toAda challenge.pr system_structure.pr


compile: generate-code
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatgcc -c *.adb
	gcc -c test.c
	gcc -o test test.o challenge.o taste_dataview.o taste_basictypes.o -lgnat -lm
	./test && echo 'All OK!'


parse:
	../../../opengeode.py challenge.pr system_structure.pr --check

coverage:
	coverage run -p ../../../opengeode.py challenge.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr test
