#!/bin/bash


./exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 357
./exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 254


cd export && ~/opt/spacecreatorenv6/Qt/6.3.1/gcc_64/libexec/qhelpgenerator -o opengeode.qch opengeode.qhp
cd export && ~/opt/spacecreatorenv6/Qt/6.3.1/gcc_64/libexec/qhelpgenerator -o opengeode.qhc opengeode.qhcp

