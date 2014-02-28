#!/usr/bin/env python

# this script is used to make a windows binary of opengeode
# on windows, make sure you have python2.7, pyside, and pip installed
# install antlr runtime this way:  pip install antlr_python_runtime
# then for this script to work you need to have a local copy of msvcp90.dll
# look for it in your windows harddisk - you will find plenty of copiess.
# then download and install py2exe
# then run python.exe setup.py py2exe -b1 -c

from distutils.core import setup

try:
    import py2exe
except ImportError:
    print('[ERROR] For a Windows installation you need to download'
          ' and install py2exe')

setup(windows=['opengeode.py'])

