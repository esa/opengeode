include ../shared.mk

all: test-ada test-llvm

edit:
	$(OPENGEODE) orchestrator.pr system_structure.pr

test-parse:
	$(OPENGEODE) orchestrator.pr system_structure.pr --check

test-ada: orchestrator.ali dataview-uniq.o | test_ada.o
	$(GNATBIND) -n orchestrator.ali
	$(GNATLINK) -o test_ada test_ada.o orchestrator.ali -lgnat
	./test_ada

test-llvm: orchestrator.o

test-python: orchestrator.ali
	$(GNATBIND) -n -Llibrorchestrator orchestrator
	$(GNATMAKE) -c b~orchestrator.adb
	$(CC) -shared -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o -lgnat
	python -c "from ctypes import *; test=CDLL('./liborchestrator.so'); test.librorchestratorinit()"

coverage:
	coverage run -p $(OPENGEODE) orchestrator.pr system_structure.pr --toAda

.PHONY: all edit test-parse test-ada test-llvm coverage
