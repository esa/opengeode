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

%.o: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --llvm
	$(LLC) $*.ll
	$(CC) -c $*.s

%.ali: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -c *.adb

%.o: %.asn FORCE
	$(ASN1SCC) -c $< -typePrefix asn1Scc -equal
	$(CC) -c $*.c

%.o: %.c FORCE
	$(CC) -c $<

FORCE:

.PHONY: clean