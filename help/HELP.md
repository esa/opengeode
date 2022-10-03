This folder contains the data for the `QHelp` engine in opengeode

The only file that opengeode needs to operate is `opengeode.qhc`. It contains all the help data in a compressed form.

To generate this file:

1) get the html input from the taste wiki

```
$ exportMediaWiki2Html.py -l http://taste.tuxfamily.org/wiki/ -g 357 
```

2) create `opengeode.qch` from this input using the qhelpgenerator tool

```
$ qhelpgenerator opengeode.qhp  -o opengeode.qch  # possibly edit the .qhp file first to match the content
```

3) create `opengeode.qhc`:

```
$ qhelpgenerator opengeode.qhcp -o opengeode.qhc  # the .qhcp file is a fixed input
```


