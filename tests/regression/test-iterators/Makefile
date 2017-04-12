include ../shared.mk

all: test-ada test-llvm

clean:
	rm -rf build
	rm -rf Makefile.properties orchestrator_stop_conditions.ad?


edit:
	$(OPENGEODE) orchestrator.pr

test-parse:
	$(OPENGEODE) orchestrator.pr --check

test-ada:
	mkdir -p build && cp *.pr *.asn model_checker.gpr properties build && cd build && \
	../../../../opengeode/opengeode.py orchestrator.pr --shared && \
	$(ASN1SCC) -Ada dataview-uniq.asn -typePrefix asn1Scc -equal && \
	taste-properties -d -s properties orchestrator.pr && \
	taste-asn1-iterators *.asn && gprbuild -Pmodel_checker && ./model_checker

simu: test-ada
	cd build && make -f Makefile.properties && \
	./orchestrator_simu.sh


test-c:
	echo 'No test for C'

test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-c simu test-llvm coverage
