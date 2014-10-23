#!/bin/bash -e

echo 'you must download and install antlr_python_runtime-3.1.3.tar.gz:
(from http://pypi.python.org/pypi/antlr_python_runtime/3.1.3 for ex)
cd /opt
sudo tar zxvf antlr_python_runtime-3.1.3.tar.gz
cd antlr_python_runtime-3.1.3
sudo python setup.py install --record install.record

To uninstall later, type:
sudo rm $(cat install.record)

You must also download and unpack antlr-3.1.3.tar.gz
'

if [ ! -d antlr-3.1.3 ]
then
    wget http://download.tuxfamily.org/taste/misc/antlr-3.1.3.tar.bz2
    tar xvf antlr-3.1.3.tar.bz2
    NO_ANTLR=1
fi
export CLASSPATH=$(pwd)/antlr-3.1.3/lib/antlr-3.1.3.jar
java org.antlr.Tool sdl92.g

if [ $NO_ANTLR ]
then
    rm -rf antlr-3.1.3
    rm antlr-3.1.3.tar.bz2
fi

