all: compile-all

test-parse:
	@$(MAKE) -s -C tests/regression $@

test-ada:
	@$(MAKE) -s -C tests/regression $@

test-llvm:
	@$(MAKE) -s -C tests/regression $@

benchmark:
	@$(MAKE) -s -C tests/regression $@

benchmark-O1:
	@$(MAKE) -s -C tests/regression $@

benchmark-O2:
	@$(MAKE) -s -C tests/regression $@

benchmark-O3:
	@$(MAKE) -s -C tests/regression $@

coverage:
	@$(MAKE) -s -C tests/regression $@

flake8:
	@echo Generating flake8_report file
	@cd opengeode && flake8 opengeode.py Pr.py sdlSymbols.py genericSymbols.py ogParser.py \
	        AdaGenerator.py Renderer.py Clipboard.py Lander.py ogAST.py \
	        undoCommands.py  Connectors.py Asn1scc.py Helper.py \
	        Statechart.py TextInteraction.py > flake8_report

compile-all:
	@pyside-rcc opengeode.qrc -o opengeode/icons.py
	@if [ ! -f antlr-3.1.3.tar.bz2 ] ; \
		then wget http://download.tuxfamily.org/taste/misc/antlr-3.1.3.tar.bz2 ; \
		tar jxvf antlr-3.1.3.tar.bz2 ; \
	fi
	@CLASSPATH=$$PWD/antlr-3.1.3/lib/antlr-3.1.3.jar java org.antlr.Tool sdl92.g
	@mv sdl92*.py opengeode

install:
	@python setup.py install --record install.record

publish: install
	@python setup.py sdist upload

freeze-linux:
	@bash -c "test -f pyinstaller-opengeode.tar.gz || wget http://download.tuxfamily.org/taste/misc/pyinstaller-opengeode.tar.gz"
	@tar zxvf pyinstaller-opengeode.tar.gz
	@cd pyinstaller-pyinstaller-953f6e3 && python pyinstaller.py ../opengeode/opengeode.py --onefile && mkdir -p ../dist-linux && mv opengeode/dist/opengeode ../dist-linux && cd ..
	@echo binary installed in ./dist-linux/

clean:
	@$(MAKE) -s -C tests/regression $@
	@find . -name '*~' | xargs rm -f
	@find . -name '*.o' | xargs rm -f
	@rm -f pyinstaller-opengeode.tar.gz
	@rm -rf dist-linux
	@rm -rf pyinstaller-pyinstaller-953f6e3
	@rm -rf opengode/*.pyc dist build *.egg-info

.PHONY: all test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 flake8 coverage compile-all install publish clean freeze-linux
