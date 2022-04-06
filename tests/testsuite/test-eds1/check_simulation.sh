#!/bin/bash -e
rm -rf testsc_simu
mkdir -p testsc_simu
cp testsc.pr dataview.asn testsc_simu
cd testsc_simu
opengeode testsc.pr --toAda
cat *.asn > dataview-uniq.asn 
asn1scc -Ada -typePrefix asn1Scc -equal dataview-uniq.asn
gnat make testsc
