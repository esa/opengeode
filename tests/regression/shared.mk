benchmark:
	@make test-ada > /dev/null 2>&1 && ([ -f test_ada ] || exit 1)
	@make test-llvm > /dev/null 2>&1 && ([ -f test_llvm ] || exit 1)
	@echo "binary-size:"
	@echo "    test_llvm: $$(du -b test_llvm | cut -f1)"
	@echo "    test_ada:  $$(du -b test_ada | cut -f1)"

clean:
	@rm -rf *.adb *.ads *.pyc runSpark.sh spark.idx *.o *.ali gnat.cfg \
	        examiner bin *.wrn *.gpr *.ll *.s dataview-uniq.c dataview-uniq.h \
	        real.c xer.c ber.c acn.c asn1crt.c asn1crt.h test_ada test_llvm

.PHONY: benchmark clean