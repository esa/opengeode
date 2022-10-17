This folder contains the data for the `QHelp` engine in opengeode

The only file that opengeode needs to operate is `opengeode.qhc`. It contains all the help data in a compressed form.

To generate this file:

1) get the html input from the taste wiki

```
./exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 357
./exportMediaWiki2Html.py --url https://taste.tuxfamily.org/wiki/ --page 254
```

2) create `opengeode.qch` from this input using the qhelpgenerator tool

```
# possibly edit the .qhp file first to match the content
cd export && ~/opt/spacecreatorenv6/Qt/6.3.1/gcc_64/libexec/qhelpgenerator -o opengeode.qch opengeode.qhp
cd export && ~/opt/spacecreatorenv6/Qt/6.3.1/gcc_64/libexec/qhelpgenerator -o opengeode.qhc opengeode.qhcp
```

