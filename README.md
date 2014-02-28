OpenGEODE
=========

OpenGEODE is a tiny open-source SDL editor that is developed for
the purpose of providing an easy to use and free state machine editor and
Ada code generator to the TASTE toolchain from the European Space Agency,
running in combination with ESA's ASN.1 "Space Certifiable" ASN.1 compiler.

SDL is the Specification and Description Language (Z100 standard from ITU-T).

This is NOT related to the graphical Simple DirectMedia Layer libraries!

Visit http://sdl-forum.org for more information about SDL.

Installation
============

Pre-requisites
--------------

There are three majors dependencies for OpenGEODE:

- Pyside (the Qt bindings for Python) and the ANTLR runtime to be
- Python ANTLR Runtime
- PyGraphviz

If you use pip to install OpenGEODE, these dependencies should be installed
automatically. However, note that installing PySide from pip requires some
work and is not straightforward.

If you are using a Linux Debian-based distribution (including Ubuntu),
I would recommended to install PySide using your package manager:
You should also install pygraphviz using the same method, for convenience.

$ sudo apt-get install python-pyside pyside-tools python-pygraphviz

And to install pip:

$ sudo apt-get install pip

The Python 2.7 ANTLR 3.1.3 runtime is not part of Debian packages. Install
it with pip (or download and install manually the package):

$ pip install antlr_python_runtime

On Windows:

You need to download and install Python, Pyside, and pip (binaries are
available on respective websites)

On FreeBSD:

PySide is available through the ports.
You can also use easy_install to install it.
Use pip to install the ANTLR runtime (see above)

Automatic installation (recommended)
------------------------------------

$ pip install singledispatch
$ pip install opengeode

This is sufficient to get opengeode running

In addition OpenGEODE is capable of generating code for embedded, real-
time systems in the Ada programming language, with compact and efficient
data manipulation and binary encoding using the ASN.1 notation.

To get the full benefits of SDL and OpenGEODE, consider installing
TASTE, that is a complete development environment dedicated to
real-time, embedded systems from the European Space Agency.

TASTE also allows the transparent integration and communication between
models developed by commercial tools such as Matlab-Simulink and 
Real-Time Developer Studio.

Installation from source
------------------------

You can get the source from the TASTE repositories or from GitHub

$ svn co https://tecsw.estec.esa.int/svn/taste/trunk/misc/opengeode opengeode

Then as root, type:

$ make install

Information and contact
=======================

OpenGEODE is part of the TASTE project.

Find more information and download at http://taste.tuxfamily.org

OpenGEODE is developed and maintained by Maxime Perrotin
maxime (dot) perrotin (at) esa (dot) int

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

0.99 (28/02/2014)
     - Refactoring of the backend engine, now using singledispatch
     - Minor bugfixes

0.98 (08/07/2014)
     - Added support for FOR loops
       In a task, use "for x in range([start], stop, [range]): ... endfor"
       or "for x in sequenceOfvariable: ... endfor"
     - Default symbol size is smaller
     - Various minor bugfixes
0.97 (07/12/2013)
     - added support for default value when declaring a variable
       e.g. DCL myVar myType ::= { x 5, y 2 };
       default value must be a ground expression

