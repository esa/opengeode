EXAMPLES=$(sort $(dir $(wildcard */)))

test-parse:
	@python test.py test-parse

test-ada:
	@python test.py test-ada

test-llvm:
	@python test.py test-llvm

coverage:
	for v in $(EXAMPLES) ; do make -C $$v coverage && mv $$v/.coverage* . \
	|| exit 1 ; done ; coverage combine

clean:
	for v in $(EXAMPLES); do make -C $$v clean ; done

.PHONY: test-parse test-ada test-llvm coverage clean
