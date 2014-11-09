OPENGEODE=../../../opengeode.py
ASN1SCC=asn1.exe
CC=gcc
LLC=llc
GNATMAKE=gnatmake
GNATBIND=gnatbind
GNATLINK=gnatlink
O=0

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm \
	       *.autosave

%.o: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --llvm -O$(O)
	$(LLC) $*.ll
	$(CC) -O$(O) -c $*.s

%.ali: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -c *.adb

%.o: %.asn FORCE
	$(ASN1SCC) -c $< -typePrefix asn1Scc -equal
	$(CC) -O$(O) -c $*.c

%.o: %.c FORCE
	$(CC) -O$(O) -c $<

FORCE:

.PHONY: clean
