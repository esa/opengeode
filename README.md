OpenGEODE
=========

OpenGEODE is a tiny open-source SDL editor that is developed for
the purpose of providing an easy to use and free state machine editor and
Ada code generator to the TASTE toolchain from the European Space Agency,
running in combination with ESA's ASN.1 "Space Certifiable" ASN.1 compiler.

SDL is the Specification and Description Language (Z100 standard from ITU-T).

This is NOT related to the graphical Simple DirectMedia Layer libraries!

Visit http://sdl-forum.org for more information about SDL.
Visit http://www.pragmadev.com to get a full-featured commercial SDL tool and support


![alt tag](icons/opengeode-screenshot.png)


Features
--------

- Graphical editor of SDL processes and procedures.
- SDL2010 features: FOR loops in task symbols, hierarchical states
- Works on pure PR+CIF files (textual SDL notation) - no fancy proprietary save format
- Full supports ASN.1 data types - using ESA Space Certified compiler (www.github.com/ttsiodras/asn1scc)
- Generates Ada code
- Extensive syntax and semantic checks
- Automatic conversion to Statechart diagrams
- Save the complete or parts of the model to PNG/SVG/PDF files
- Hyperlinks (link a symbol content to any external document or web page)
- Zoom in, zoom-out
- Context-dependent text auto-completion
- Syntax highlighting
- Undo/Redo, Copy-Paste
- (Limited) VIM mode - You can use :wq or :%s,search,replace,g, and /search pattern
- SDL to LLVM code generation
- Python API to parse and render SDL from other Python modules

Installation
============

On Windows, download the binary from [here](http://download.tuxfamily.org/taste/opengeode_windows.zip)

Uzip it and run opengeode.exe. It contains everything without any other external dependencies.

Linux Pre-requisites
--------------------

There are several dependencies for OpenGEODE:

- Python 2.7 with pip
- Pyside (the Qt bindings for Python)
- Python ANTLR Runtime
- PyGraphviz
- enum34, singledispatch
- [ASN1SCC](https://github.com/ttsiodras/asn1scc)
- (optional) GNAT to build the generated Ada code
- mono
- llvmpy (tested with 0.12.7)
- LLVM (tested with 3.3)

On Debian, Ubuntu, and probably other distributions:

```bash
$ sudo apt-get install python-pyside pyside-tools graphviz python-pip gnat libmono-system-runtime4.0-cil \
               libmono-corlib4.0-cil libmono-system-runtime-serialization-formatters-soap4.0-cil libmono-system-web4.0-cil \
               libmono-system-xml4.0-cil libmono-system4.0-cil mono-runtime libmono-system-numerics4.0-cil \
               libmono-system-data-linq4.0-cil libmono-corlib2.0-cil libmono-system2.0-cil
$ sudo pip install --upgrade graphviz enum34 singledispatch
$ sudo pip install antlr_python_runtime --allow-external antlr_python_runtime --allow-unverified antlr_python_runtime
```

To install the ASN.1 compiler:

```bash
$ cd /opt
$ sudo wget http://download.tuxfamily.org/taste/ASN1SCC/ASN1SCC-latest.tgz
$ sudo tar zxvf asn1Comp.tar.gz
$ echo 'export PATH=$PATH:/opt/<path to latest ASN1SCC>/bin' >> ~/.bashrc
```

Check that it works:

```bash
$ asn1.exe
```

Optionally, to install llvmpy and LLVM follow the instructions [here](http://www.llvmpy.org/llvmpy-doc/0.12.7/doc/getting_started.html#installation)

OpenGEODE installation
----------------------

To install the application on your machine, once all dependencies are met:

```bash
$ pip install --upgrade opengeode
```

This is sufficient to get opengeode running

Installation from source
------------------------

You can get the source from the TASTE repositories or from GitHub

```bash
$ git clone https://github.com/maxime-esa/opengeode.git
```

Then enter the opengeode directory and as root, type:

```bash
$ make install
```

Installation is optional. You can simply run opengeode.py to get it work.

Information and contact
=======================

OpenGEODE is part of the TASTE project.

Find more information and download at http://taste.tuxfamily.org

TASTE allows to create embedded software systems that combine SDL models with C, Ada,
Matlab-Simulink and a few other languages or tools.

OpenGEODE is mainly designed, developed and maintained by Maxime Perrotin
maxime (dot) perrotin (at) esa (dot) int

The LLVM backend was designed and implemented by Diego Barbera during the ESA Summer of Code 2014

Some parts have been implemented by Laurent Meyer (native SDL type support in the parser)

The background pattern was downloaded from www.subtlepatterns.com

The ASN.1 compiler (ASN1Scc) that OpenGEODE is based on was
developed by George Mamais and Thanassis Tsiodras for the European
Space Agency. Information at http://www.semantix.gr/asn1scc

Licence
=======

License is LGPL (see file LICENSE)
The fonts are the fonts from Ubuntu, check licence in file FONT-LICENSE.TXT

Changelog
=========

1.0.0 (06/2015)
     - Bugfixes and minor improvements
     - Python API / Simulator function (coupled with other TASTE components)

1.0RC (10/2014) 
     - Release candidate Version 1
     - Allow standalone systems (made of one process)
     - Major refactoring of parser and Ada backend
     - Many bugfixes and improvements
     - First version of LLVM backend

0.994 (07/2014)
     - Maintenance release, minor fixes

0.993 (07/2014)
     - Parser bugfixes
     - Better support for nested states
     - Ada generator improvements
     - Support for unicode
     - Indentation of PR code
     - Copy-paste of procedures and nested states
     - Improved regression testing

0.99 (04/2014)
     - Refactoring of the backend engine, now using singledispatch
     - Support of hierachical states
     - Minor bugfixes


0.98
     - Added support for FOR loops
       In a task, use "for x in range([start], stop, [range]): ... endfor"
       or "for x in sequenceOfvariable: ... endfor"
     - Default symbol size is smaller
     - Various minor bugfixes


0.97
     - added support for default value when declaring a variable
       e.g. DCL myVar myType ::= { x 5, y 2 };
       default value must be a ground expression

