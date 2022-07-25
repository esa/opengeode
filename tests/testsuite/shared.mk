OPENGEODE=opengeode
SDL2IF=sdl2if
ASN1SCC=asn1scc
CC=gcc
LLC=llc
GNATMAKE=gnatmake -gnat2012
GNATBIND=gnatbind
GNATLINK=gnatlink -lgcov -coverage 
O=0
TESTQGEN_PARSE=../testqgen.py test-qgen-parse
TESTQGEN_ADA=../testqgen.py test-qgen-ada
TESTQGEN_C=../testqgen.py test-qgen-c
TESTQGEN_GT_ADA=../testqgen.py test-qgen-gt-ada
TESTQGEN_GT_C=../testqgen.py test-qgen-gt-c

clean:
	gnat clean *.adb
	rm -rf *.if *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.so *.ali gnat.cfg \
	       examiner bin *.wrn GPS_project.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	       real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm \
	       *.autosave *_simu.sh *_interface.aadl *.lst *.gcno *.gcda *.gcov \
	       check obj src code *_datamodel.asn asn1_x86.gpr *_ada.gpr *.pml

test-promela: FORCE
	 sdl2promela --sdl *.pr -o og.pml

%.o: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --llvm -O$(O)
	$(LLC) $*.ll
	$(CC) -O$(O) -c -g $*.s

%.c: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toC
	$(ASN1SCC) -c -typePrefix asn1Scc -equal dataview-uniq.asn 

%.if: %.pr FORCE
	$(SDL2IF) $< ${STRUCT}

%.ali: %.pr FORCE
	$(OPENGEODE) $< system_structure.pr --toAda && \
	$(ASN1SCC) -Ada -typePrefix asn1Scc -equal *.asn && \
	$(GNATMAKE) -O$(O) -c -g -fprofile-arcs -ftest-coverage *.adb

%.o: %.asn FORCE
	$(ASN1SCC) -c -typePrefix asn1Scc -equal $<  
	$(CC) -O$(O) -c -g $*.c

%.o: %.c FORCE
	$(CC) -O$(O) -c -g $<

FORCE:

.PHONY: clean
