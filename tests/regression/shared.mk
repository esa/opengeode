benchmark:
	@python ../benchmark.py .

clean:
	@rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg \
	        examiner bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	        real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: benchmark clean