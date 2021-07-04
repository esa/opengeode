all:
	@echo [-] Run \"make dependencies\" to install all dependencies
	@echo [-] then \"make install\" to install to ~/.local/bin
	@echo [-] or \"make full-install\" that combines both
	@echo [!] IMPORTANT: make sure ~/.local/bin is in your PATH

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
	sudo apt install python3-pyside2.* || echo 'PySide2 is not available in your system. Try to run "sudo pip3 install --user --upgrade pyside2'
	sudo apt install python3-antlr3
	sudo apt install pyside2-tools || :
	#apt install python3-matplotlib
	sudo apt install python3-pygraphviz
	sudo apt install python3-stringtemplate3
	sudo apt install python3-singledispatch
	# install ASN1SCC in ~/.local/bin
	mkdir -p ~/.local/bin
	cd ~/.local ; wget -q -O - https://github.com/ttsiodras/asn1scc/releases/download/4.2.4.7f/asn1scc-bin-4.2.4.7f.tar.bz2 | tar jxpvf - ; cd bin ; ln -s ../asn1scc/* .
	echo [-] IMPORTANT: Make sure that ~/.local/bin is in your PATH

install:
	@pip3 install --user --upgrade .

full-install: update
	sudo $(MAKE) dependencies
	$(MAKE) install

publish: 
	@rm -f dist/*
	@python3 setup.py sdist bdist_wheel
	@twine upload dist/*

pytest:
	# make sure you have installed pytest-qt:
	# pip3 install --user --upgrade pytest-qt
	cd tests/pytests && py.test

clean:
	@$(MAKE) -s -C tests/testsuite $@
	@find . -name '*~' | xargs rm -f
	@find . -name '*.o' | xargs rm -f
	@rm -f pyinstaller-opengeode.tar.gz
	@rm -rf dist-linux
	@rm -rf pyinstaller-pyinstaller-953f6e3
	@rm -rf opengode/*.pyc dist build *.egg-info

.PHONY: all test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 flake8 coverage compile-all install publish clean
