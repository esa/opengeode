#!/bin/bash -e
make test-python
rm -rf simu
mkdir -p simu
asn2aadlPlus dataview-uniq.asn simu/DataView.aadl
cp libog.so dataview-uniq.asn *.pr simu
mv *.aadl simu
cd simu
aadl2glueC DataView.aadl orchestrator_interface.aadl
asn2dataModel -toPython dataview-uniq.asn
make -f Makefile.python
echo "errCodes=$(taste-asn1-errCodes ./dataview-uniq.h)" >>datamodel.py 
LD_LIBRARY_PATH=. taste-gui -l
