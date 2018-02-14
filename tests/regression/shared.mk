OPENGEODE=../../../opengeode/opengeode.py
ASN1SCC=`which asn1.exe`
CC=gcc
LLC=llc
GNATMAKE=gnatmake -gnat2012
GNATBIND=gnatbind
GNATLINK=gnatlink -lgcov -coverage 
O=0

clean:
	rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check

%.o: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --llvm -O$(O)
	$(LLC) $*.ll
	$(CC) -O$(O) -c -g $*.s

%.c: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toC
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn 

%.ali: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toAda && \
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn && \
	$(GNATMAKE) -O$(O) -gnat2012 -c -g -fprofile-arcs -ftest-coverage *.adb

%.o: %.asn FORCE
	mono $(ASN1SCC) -c -typePrefix asn1Scc -equal $<  
	$(CC) -O$(O) -c -g $*.c

%.o: %.c FORCE
	$(CC) -O$(O) -c -g $<

FORCE:

.PHONY: clean
