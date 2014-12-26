gnatmake -c orchestrator.adb
gnatbind -n -Lliborchestrator orchestrator
gnatmake -c b~orchestrator.adb
gcc -shared -fPIC -o liborchestrator.so b~orchestrator.o orchestrator.o taste_basictypes.o adaasn1rtl.o -lgnat
