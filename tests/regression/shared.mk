OPENGEODE=../../../opengeode/opengeode.py
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
	       *.autosave *_simu.sh *_interface.aadl *.lst

%.o: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --llvm -O$(O)
	$(LLC) $*.ll
	$(CC) -O$(O) -c -g $*.s

%.ali: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toAda
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal
	$(GNATMAKE) -O$(O) -gnat2012 -c -g *.adb

%.o: %.asn FORCE
	$(ASN1SCC) -c $< -typePrefix asn1Scc -equal
	$(CC) -O$(O) -c -g $*.c

%.o: %.c FORCE
	$(CC) -O$(O) -c -g $<

FORCE:

.PHONY: clean
