#!/bin/bash -e
rm -rf testsc_simu
mkdir -p testsc_simu
cp /home/taste/opengeode-github/tests/regression/test-eds1/testsc_simu/testsc.pr /home/taste/opengeode-github/tests/regression/test-eds1/testsc_simu/dataview.asn testsc_simu
cd testsc_simu
opengeode testsc.pr --shared
cat /home/taste/opengeode-github/tests/regression/test-eds1/testsc_simu/dataview.asn >> dataview-uniq.asn 
mono $(which asn1.exe) -Ada -typePrefix asn1Scc -equal /home/taste/opengeode-github/tests/regression/test-eds1/testsc_simu/dataview.asn
mono $(which asn1.exe) -c -typePrefix asn1Scc -equal /home/taste/opengeode-github/tests/regression/test-eds1/testsc_simu/dataview.asn
gnatmake -fPIC -gnat2012 -c *.adb
gnatbind -n -Llibtestsc testsc
gnatmake -fPIC -c -gnat2012 b~testsc.adb
gcc -shared -fPIC -o libtestsc.so b~testsc.o testsc.o ccsdssoissubnetwork.o ccsdssoissubnetworkinterfaces.o demo.o demointerfaces.o environment.o environmentinterfaces.o adaasn1rtl.o -lgnat
rm -f dataview-uniq.c dataview-uniq.h
asn2aadlPlus dataview-uniq.asn DataView.aadl
aadl2glueC DataView.aadl testsc_interface.aadl
asn2dataModel -toPython dataview-uniq.asn
make -f Makefile.python
echo "errCodes=$(taste-asn1-errCodes ./dataview-uniq.h)" >>datamodel.py
LD_LIBRARY_PATH=. opengeode-simulator
