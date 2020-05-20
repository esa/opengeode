all: compile-all

test-parse:
	@$(MAKE) -s -C tests/testsuite $@

test-ada:
	@$(MAKE) -s -C tests/testsuite $@

test-llvm:
	@$(MAKE) -s -C tests/testsuite $@

benchmark:
	@$(MAKE) -s -C tests/testsuite $@

benchmark-O1:
	@$(MAKE) -s -C tests/testsuite $@

benchmark-O2:
	@$(MAKE) -s -C tests/testsuite $@

benchmark-O3:
	@$(MAKE) -s -C tests/testsuite $@

coverage:
	@$(MAKE) -s -C tests/testsuite $@

flake8:
	@echo Generating flake8_report file
	@cd opengeode && flake8 opengeode.py Pr.py sdlSymbols.py genericSymbols.py ogParser.py \
	        AdaGenerator.py Renderer.py Clipboard.py Lander.py ogAST.py \
	        undoCommands.py  Connectors.py Asn1scc.py Helper.py \
	        Statechart.py TextInteraction.py > flake8_report

compile-all:
	@pyside2-rcc opengeode.qrc -o opengeode/icons.py
	# use antlr3 from Debian's python3-antlr3 package
	antlr3 -o opengeode sdl92.g

update:
	git pull

dependencies:
	apt install python3-pyside2.*
	apt install python3-antlr3
	apt install pyside2-tools
	#apt install python3-matplotlib
	apt install python3-pygraphviz
	apt install python3-stringtemplate3
	apt install python3-singledispatch
	
	# optional dependencies from taste: spedometer, properties, dmt, pymsc, asn1-value-editor

install:
	@pip3 install --user --upgrade .

full-install: update dependencies install

publish: 
	@python3 setup.py sdist upload

pytest:
	# make sure you have installed pytest-qt:
	# pip3 install --user --upgrade pytest-qt
	cd tests/pytests && py.test

freeze-linux:
	@bash -c "test -f pyinstaller-opengeode.tar.gz || wget http://download.tuxfamily.org/taste/misc/pyinstaller-opengeode.tar.gz"
	@tar zxvf pyinstaller-opengeode.tar.gz
	@cd pyinstaller-pyinstaller-953f6e3 && python pyinstaller.py ../opengeode/opengeode.py --onefile && mkdir -p ../dist-linux && mv opengeode/dist/opengeode ../dist-linux && cd ..
	@echo binary installed in ./dist-linux/

clean:
	@$(MAKE) -s -C tests/testsuite $@
	@find . -name '*~' | xargs rm -f
	@find . -name '*.o' | xargs rm -f
	@rm -f pyinstaller-opengeode.tar.gz
	@rm -rf dist-linux
	@rm -rf pyinstaller-pyinstaller-953f6e3
	@rm -rf opengode/*.pyc dist build *.egg-info

.PHONY: all test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 flake8 coverage compile-all install publish clean freeze-linux
