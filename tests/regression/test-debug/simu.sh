#!/bin/sh
make test-python
rm -rf simu
mkdir -p simu
asn2aadlPlus.py dataview-uniq.asn simu/DataView.aadl
cp liborchestrator.so dataview-uniq.asn simu
mv *.aadl simu
cd simu
aadl2glueC.py DataView.aadl orchestrator_interface.aadl
asn2dataModel.py -toPython dataview-uniq.asn
make -f Makefile.python
echo "errCodes=$(python $(taste-config --prefix)/share/asn1-editor/errCode.py ./dataview-uniq.h)" >>datamodel.py 
LD_LIBRARY_PATH=. taste_gui -l
