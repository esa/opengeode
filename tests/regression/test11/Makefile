all: compile

generate-code:
	../../../opengeode.py --toAda og.pr system_structure.pr


compile: generate-code
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	gcc -c test.c
	gcc -o test test.o og.o taste_dataview.o -lgnat
	./test > result
	diff result expected && echo 'All OK!'
	

parse:
	../../../opengeode.py og.pr system_structure.pr --check

coverage:
	coverage run -p ../../../opengeode.py og.pr system_structure.pr --toAda

clean:
	rm -rf result *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr
