EXAMPLES=$(sort $(dir $(wildcard */)))

coverage:
	for v in $(EXAMPLES) ; do make -C $$v coverage && mv $$v/.coverage* . \
	|| exit 1 ; done ; coverage combine

clean:
	for v in $(EXAMPLES); do make -C $$v clean ; done

.PHONY: coverage clean
