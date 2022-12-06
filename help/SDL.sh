#!/bin/bash
echo set NO_DL=1 to avoid re-downloading all files
if [ -z $NO_DL ]
then
    git clone https://github.com/maxime-esa/exportMediaWiki2Html
    exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 357
    exportMediaWiki2Html/exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 254
fi

cp opengeode.qhp export
cp opengeode.qhcp export
cd export
spacecreator.AppImage --qhelpgenerator -o opengeode.qch opengeode.qhp
spacecreator.AppImage --qhelpgenerator -o opengeode.qhc opengeode.qhcp
mv opengeode.qch ..
mv opengeode.qhc ..

