#!/bin/bash -e
make test-python
rm -rf simu
mkdir -p simu
asn2aadlPlus dataview.asn simu/DataView.aadl
cp libog.so dataview.asn *.pr simu
mv *.aadl simu
cd simu
aadl2glueC DataView.aadl og_interface.aadl
asn2dataModel -toPython dataview.asn
make -f Makefile.python
echo "errCodes=$(taste-asn1-errCodes ./dataview.h)" >>datamodel.py 
LD_LIBRARY_PATH=. opengeode-simulator
