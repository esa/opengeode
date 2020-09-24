#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Setup file for Linux distribution
Usage:  python3 setup.py sdist bdist_wheel --> to create a tarball
        pip3 install --user --upgrade .    --> to install in ~/.local
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
    description='A free SDL editor for TASTE',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    tests_require=['tabulate'],
    include_package_data=True,
    url='http://opengeode.net',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': [
            'opengeode = opengeode.opengeode:opengeode'
        ]
    },
)
