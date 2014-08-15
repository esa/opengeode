EXAMPLES=test1 test2 test3 test4 test5 test6 test7 test8 test9 test10 \
         test11 test12 test-substrings test-expressions test-controlflow \
         test-exitnested test-operators

coverage:
	for v in $(EXAMPLES) ; do make -C $$v coverage && mv $$v/.coverage* . \
	|| exit 1 ; done ; coverage combine

clean:
	for v in $(EXAMPLES); do make -C $$v clean ; done
