benchmark:
	@$(MAKE) test-ada > /dev/null 2>&1 && ([ -f test_ada ] || exit 1)
	@$(MAKE) test-llvm > /dev/null 2>&1 && ([ -f test_llvm ] || exit 1)
	@echo "binary-size:"
	@echo "    test_llvm: $$(du -b test_llvm | cut -f1)"
	@echo "    test_ada:  $$(du -b test_ada | cut -f1)"

.PHONY: benchmark