#!/bin/bash

git clone https://github.com/maxime-esa/exportMediaWiki2Html
exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 357
exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 254

cp opengeode.qhp export
cp opengeode.qhcp export
cd export && qhelpgenerator -o opengeode.qch opengeode.qhp
cd export && qhelpgenerator -o opengeode.qhc opengeode.qhcp

