#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Setup file for Linux distribution
Usage:  python setup.py sdist   --> to create a tarball
        python setup.py install --> to install in python directory
'''
# from distutils.core import setup

from setuptools import setup, find_packages

import opengeode

setup(
    name='opengeode',
    version=opengeode.__version__,
    packages=find_packages(),
    author='Maxime Perrotin',
    author_email='maxime.perrotin@esa.int',
    description='A tiny, free SDL editor for TASTE',
    long_description=open('README.md').read(),
    install_requires=[],
    tests_require=['tabulate'],
    include_package_data=True,
    url='http://opengeode.net',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'opengeode = opengeode.opengeode:opengeode'
        ]
    },
)
