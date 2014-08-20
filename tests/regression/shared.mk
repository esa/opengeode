OPENGEODE=../../../opengeode.py
ASN1SCC=asn1.exe
CC=gcc
LLC=llc
GNATMAKE=gnatmake
GNATBIND=gnatbind
GNATLINK=gnatlink

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg \
	       examiner bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm \
	       *.autosave

.PHONY: clean