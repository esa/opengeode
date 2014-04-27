all: compile

generate-code:
	../../../opengeode.py --toAda fce.pr system_structure.pr


compile: generate-code
	asn1.exe -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	gnatmake -c fce.adb && echo 'All OK!'

parse:
	../../../opengeode.py fce.pr system_structure.pr --check

coverage:
	coverage run -p ../../../opengeode.py fce.pr system_structure.pr --toAda

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg examiner bin *.wrn *.gpr
