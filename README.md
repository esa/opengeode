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
- SDL2010 features: state composition and state aggregation
- Works on pure PR+CIF files (textual SDL notation)
- Supports ASN.1 data types - using ESA Space Certified compiler (www.github.com/ttsiodras/asn1scc)
- Generates Ada code
- Automatic conversion to Statechart diagrams
- Save the complete or parts of the model to PNG/SVG/PDF files
- Hyperlinks (link a symbol content to any external document or web page)
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

To install OpenGEODE on Linux you need to install some system-level dependencies:

- Python 2.7 with pip (installed by default on nearly all Linux distributions)
- Pyside
- Graphviz
- [ASN1SCC](https://github.com/ttsiodras/asn1scc)
- GNAT

And optionally llvm and llvmpy

On Debian, Ubuntu, and probably other distributions:

```bash
$ sudo apt-get install pkg-config python-pyside pyside-tools graphviz \
                       graphviz-dev libgraphviz-dev  python-pip gnat-4.8 \
                       libmono-system-runtime4.0-cil libmono-corlib4.0-cil \
                       libmono-system-runtime-serialization-formatters-soap4.0-cil \
                       libmono-system-web4.0-cil libmono-system-xml4.0-cil \
                       libmono-system4.0-cil mono-runtime libmono-system-numerics4.0-cil \
                       libmono-system-data-linq4.0-cil libmono-corlib2.0-cil libmono-system2.0-cil
```

To install the ASN.1 compiler:

```bash
$ cd /opt
$ wget http://download.tuxfamily.org/taste/ASN1SCC/ASN1SCC-latest.tgz
$ tar zxvf ASN1SCC-latest.tgz
$ echo 'export PATH=$PATH:/opt/asn1scc' >> ~/.bashrc
```

Open a new terminal and check that it works:

```bash
$ mono /opt/asn1scc/asn1.exe
```

Optionally, to install llvmpy and LLVM follow the instructions [here](http://www.llvmpy.org/llvmpy-doc/0.12.7/doc/getting_started.html#installation)


OpenGEODE installation
----------------------

Make sure all dependencies are installed.

If you see a certificate error, you may need to run the following commands:

```bash
$ echo -n | openssl s_client -connect gitrepos.estec.esa.int:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > gitrepos.cert
$ sudo cp gitrepos.cert /usr/local/share/ca-certificates/gitrepos.crt
$ sudo update-ca-certificate
```

Then you can get the software with git:

```bash
$ git clone --recursive https://github.com/maxime-esa/opengeode.git
```

And install it:

```bash
$ cd opengeode
$ make install
```


Information and contact
=======================

OpenGEODE is part of the [TASTE project](http://taste.tuxfamily.org)

For additional information please contact:
maxime (dot) perrotin (at) esa (dot) int


The LLVM backend was designed and implemented by Diego Barbera during the ESA
Summer of Code 2014.
Some parts implemented by Laurent Meyer (native SDL type support in the parser)


The ASN.1 compiler (ASN1Scc) that OpenGEODE is based on was
developed by George Mamais and Thanassis Tsiodras for the European
Space Agency. Information at https://github.com/ttsiodras/asn1scc

Licence
=======

License is LGPL (see file LICENSE)
There is no runtime, and the generated code is not subject to any license.

The fonts are the fonts from Ubuntu, check licence in file FONT-LICENSE.TXT
The background pattern was downloaded from www.subtlepatterns.com

Changelog
=========

1.3.26 (05/2016)
    - Fix parser issues with negative expressions

1.3.25 (05/2016)
    - Fix reporting of syntax errors in state aggregations

1.3.22 (05/2016)
    - Bug fix in range checks for division and subtraction
    - Optimise loading when there are no CIF comments

1.3.21 (05/2016)
    - Complete support of optional fields
      (check tests/regression/test-optionalfields)

1.3.20 (05/2016)
    - Improve simulator interface

1.3.19 (04/2016)
    - Various bugfixes with ternary operator
    - Added demo "test-save" showing how to emulate the behaviour of the SAVE
      symbol
    - ASN.1 types are shown with SDL-syntax (no hyphens)

1.3.18 (04/2016)
    - Add support for value notation of NULL type
    - Remove warning when accessing CHOICE fields

1.3.17 (04/2016)
    - Add support for value notation of empty SEQUENCEs ("{}")

1.3.16 (03/2016)
    - Bugfix in testing aggregation states in the GUI

1.3.15 (03/2016)
    - Bugfix in Ada backend when a state aggregation contained only empty
      states (directly returning states).

1.3.14
    - Minor bugfix with command line handling

1.3.13
    - Bugfix in rendering of Continuous signals

1.3.12
    - Render properly parameterless procedures that are declared in the .pr
      file but without a textbox
    - When going to parent scene, fixed rendering issue

1.3.11
    - Parser is more tolerant to incomplete systems

1.3.9/10 (01/2016)
    - Checker verifies that decision coverage is complete on Real and Boolean
      types
    - F3 generates Ada code

1.3.8 (01/2016)
    - Fix logging when LLVM is not installed

1.3.7 (12/2015)
    - Added icon to use Continuous Signals from the GUI

1.3.6 (11/2015)
     - Support external procedures having a return statement
       this allows to import math functions from the libmath without having
       to provide manual code. see test-math

1.3.5 (11/2015)
     - Better support for continous signals

1.3.4 (11/2015)
     - Early support for continous signals
     - Regression issue fixed (test-nocif2)

1.3.3 (11/2015)
     - Better support of platform-dependent screen resolution and dpi
     - Minor fixes in statechart scenes (no negative coordinates)

1.3.1 (11/2015)
     - Support for State Aggregations (parallel states)
     - Improved statechart rendering

1.2.10 (10/2015)
     - Better support of renamePolicy
     - Better handling of models without CIF coordinates
     - Minor bug fixes
     - Forloop syntax error handled correctly when using range
     - support Hex and bit string literals when working with OCTET STRING
     - support OUT keyword for procedure FPAR

1.2.4 (07/2015)
     - Use version 3.2.x of the ASN1SCC compiler with new -renamePolicy flag
     - Improve robustness

1.1.1 (07/2015)
     - Strongly report syntax errors with symbol location and warning if user
       tries to save a model with syntax errors

1.1.0 (07/2015)
     - Write/Writeln procedure support enumerated types

1.0.1 (06/2015)
     - Bugfix: use mono when calling asn1.exe by default (needed redhat-based
                                                          distros)

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

