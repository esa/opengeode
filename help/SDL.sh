#!/bin/bash

git clone https://github.com/maxime-esa/exportMediaWiki2Html
exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 357
exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 254

cp opengeode.qhp export
cp opengeode.qhcp export
cd export
spacecreator.AppImage --qhelpgenerator -o opengeode.qch opengeode.qhp
spacecreator.AppImage --qhelpgenerator -o opengeode.qhc opengeode.qhcp

