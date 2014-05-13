all: compile

generate-code:
	../../../opengeode.py --toAda trafficlight.pr system_structure.pr


compile: generate-code
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c *.adb
	#gcc -c test.c
	gnatbind -n trafficlight.ali
	#gnatlink -o testcase test.o trafficlight.ali -lgnat -lm


parse:
	../../../opengeode.py trafficlight.pr system_structure.pr --check

coverage:
	coverage run -p ../../../opengeode.py trafficlight.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr test
