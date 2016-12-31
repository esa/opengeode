include ../shared.mk

all: test-ada test-llvm

clean:
	rm -rf build

edit:
	$(OPENGEODE) orchestrator.pr

test-parse:
	$(OPENGEODE) orchestrator.pr --check

test-ada:
	mkdir -p build && cp *.pr test.adb *.asn properties build && cd build && \
	../../../../opengeode/opengeode.py orchestrator.pr --shared && \
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal && \
	taste-properties -d -s properties orchestrator.pr && \
	gnat make test && ./test

simu: test-ada
	cd build && make -f Makefile.properties && \
	./orchestrator_simu.sh


test-c:
	echo 'No test for C'

test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-c simu test-llvm coverage
