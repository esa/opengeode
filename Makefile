all:
	@echo [-] Run \"make dependencies\" to install all dependencies
	@echo [-] then \"make install\" to install to ~/.local/bin
	@echo [-] or \"make full-install\" that combines both
	@echo [!] IMPORTANT: make sure ~/.local/bin is in your PATH

test-parse:
	@$(MAKE) -s -C tests/testsuite $@

test-ada:
	@PATH=~/.local/bin:"${PATH}" $(MAKE) -s -C tests/testsuite $@

test-if:
	@PATH=~/.local/bin:"${PATH}" $(MAKE) -s -C tests/testsuite $@

test-promela:
	@PATH=~/.local/bin:"${PATH}" $(MAKE) -s -C tests/testsuite $@

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
	        AdaGenerator.py Renderer.py Clipboard.py Lander.py ogAST.py sdlHelp.py \
	        undoCommands.py  Connectors.py Asn1scc.py Helper.py \
	        Statechart.py TextInteraction.py > flake8_report

compile-all:
	# use antlr3 from Debian's python3-antlr3 package
	antlr3 -o opengeode sdl92.g

update:
	git pull


~/.local/bin/asn1scc:
	# install ASN1SCC in ~/.local/bin
	mkdir -p ~/.local/bin
	cd ~/.local ; wget -q -O - https://github.com/ttsiodras/asn1scc/releases/download/4.5.0.0/asn1scc-bin-4.5.0.0.tar.bz2 | tar jxpvf - ; cd bin ; ln -s ../asn1scc/* .
	echo [-] IMPORTANT: Make sure that ~/.local/bin is in your PATH

antlr3_python3_runtime_3.4/setup.py:  | dependencies
	# python3-antlr3 runtime is not available in any official repo, taking in from TASTE
	wget -q -O - https://download.tuxfamily.org/taste/antlr3_python3_runtime_3.4.tar.bz2 | tar jxpvf -
	cd antlr3_python3_runtime_3.4 ; python3 -m pip install --user --upgrade .

pip-packages: antlr3_python3_runtime_3.4/setup.py | dependencies
	# Note : these could be installed via setup.py or requirements.txt
	# installing pyside6 through pip because of bugs with QML in the Debian bullseye release
	python3 -m pip install --user --upgrade pyside6 pygraphviz stringtemplate3 singledispatch

dependencies: ~/.local/bin/asn1scc
	sudo apt install -y python3 python3-pip libgl1 gnat python3-pexpect graphviz libgraphviz-dev

opengeode/icons.py: opengeode.qrc pip-packages
	PATH="${HOME}/.local/bin:${PATH}" pyside6-rcc opengeode.qrc -o opengeode/icons.py

install: opengeode/icons.py pip-packages
	python3 -m pip install --user --upgrade .

full-install: update
	$(MAKE) dependencies
	$(MAKE) pip-packages
	$(MAKE) install

publish: 
	@rm -f dist/*
	@python3 setup.py sdist bdist_wheel
	@twine upload dist/*

pytest:
	python3 -m pip  install --user --upgrade pytest pytest-qt
	PATH=~/.local/bin:"${PATH}" ; cd tests/pytests ; PYTEST_QT_API=PySide6 py.test

clean:
	@$(MAKE) -s -C tests/testsuite $@
	@find . -name '*~' | xargs rm -f
	@find . -name '*.o' | xargs rm -f
	@rm -f pyinstaller-opengeode.tar.gz
	@rm -rf dist-linux
	@rm -rf pyinstaller-pyinstaller-953f6e3
	@rm -rf opengeode/*.pyc dist build *.egg-info

.PHONY: all test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 flake8 coverage compile-all install publish clean
