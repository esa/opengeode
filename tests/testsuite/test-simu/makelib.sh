gnatmake -c -g -gnat2012 orchestrator.adb
gnatbind -n -Lliborchestrator orchestrator
gnatmake -c -g -gnat2012 b~orchestrator.adb
gcc -c -g external_proc.c
gcc -shared -fPIC -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o external_proc.o adaasn1rtl.o -lgnat
