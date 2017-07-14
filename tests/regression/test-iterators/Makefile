include ../shared.mk
ARCH := $(shell getconf LONG_BIT)
all: test-ada test-llvm

clean:
	rm -rf build
	rm -rf Makefile.properties orchestrator_stop_conditions.ad?


edit:
	$(OPENGEODE) orchestrator.pr

test-parse:
	$(OPENGEODE) orchestrator.pr --check

test-qgen-parse:
	$(TESTQGEN) orchestrator.pr

test-ada:
	[ $(ARCH) == 64 ] && EXTRAFLAG="--target=x86_64-linux" ; \
	mkdir -p build && cp *.pr *.asn model_checker.gpr properties build && cd build && \
	../../../../opengeode/opengeode.py orchestrator.pr --shared && \
	mono $(ASN1SCC) -Ada -typePrefix asn1Scc -equal dataview-uniq.asn && \
	taste-properties -d -s properties orchestrator.pr && \
	taste-asn1-iterators *.asn && gprbuild -Pmodel_checker $$EXTRAFLAG && ./model_checker

simu: test-ada
	cd build && make -f Makefile.properties && \
	./orchestrator_simu.sh


test-c:
	echo 'No test for C'

test-llvm: orchestrator.o

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-c simu test-llvm coverage
