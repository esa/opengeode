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
	        AdaGenerator.py Renderer.py Clipboard.py Lander.py ogAST.py ogASTDumper.py \
			sdlHelp.py undoCommands.py  Connectors.py Asn1scc.py Helper.py \
	        Statechart.py TextInteraction.py > flake8_report

compile-all:
	# use antlr3 from Debian's python3-antlr3 package
	antlr3 -o opengeode sdl92.g

update:
	git pull

# Define the expected version of the QtTaste widget
export QTASTE_VERSION=1.2.7

dependencies:
	#sudo apt install -y python3 python3-pip libgl1 gnat python3-pexpect xcb libxcb-cursor0
	# installing pyside6 through pip because of bugs with QML in the Debian bullseye release
	python3 -c 'import PySide6' || python3 -m pip install pyside6
	# python3-antlr3 runtime is not available in any official repo, taking in from TASTE
	python3 -c 'import antlr3' || python3 -m pip install https://download.tuxfamily.org/taste/antlr3_python3_runtime_3.4.tar.bz2 
	python3 -c 'import pygraphviz' || python3 -m pip install pygraphviz
	# install ASN1SCC in ~/.local/bin
	mkdir -p ~/.local/bin
	asn1scc -v || (cd ~/.local ; wget -q -O - https://github.com/maxime-esa/asn1scc/releases/download/4.5.2.3/asn1scc-bin-4.5.2.3.tar.bz2 | tar jxpvf - ; cd bin ; ln -sf ../asn1scc/* .)
	# install the requirement and review widget
	@echo "[-] Building Requirements and Review (optional widget)"
	@python3 -c "import sys, PyTasteQtWidgets as taste, os; sys.exit(taste.__version__!=os.environ['QTASTE_VERSION'])" || \
	       (rm -rf TasteQtWidgets && \
	       git clone --depth 1 --branch ${QTASTE_VERSION} https://github.com/esa/TasteQtWidgets && \
	       cd TasteQtWidgets/pytastewidgets && python3 ./install.py > /dev/null || exit 1)
	@echo [-] IMPORTANT: Make sure that ~/.local/bin is in your PATH

install:
	PATH=~/.local/bin:"${PATH}" pyside6-rcc opengeode.qrc -o opengeode/icons.py && python3 -m pip install --upgrade .

full-install: update
	$(MAKE) dependencies
	$(MAKE) install

publish: 
	@rm -f dist/*
	@python3 setup.py sdist bdist_wheel
	@twine upload dist/*

pytest:
	python3 -m pip  install --user --upgrade pytest pytest-qt
	PATH=~/.local/bin:"${PATH}" ; cd tests/pytests ; PYTEST_QT_API=PySide6 py.test

help:
	# Build the inline help by getting the content on the wiki and converting it to QtHelp format
	cd help && ./SDL.sh

clean:
	@$(MAKE) -s -C tests/testsuite $@
	@find . -name '*~' | xargs rm -f
	@find . -name '*.o' | xargs rm -f
	@rm -f pyinstaller-opengeode.tar.gz
	@rm -rf dist-linux
	@rm -rf pyinstaller-pyinstaller-953f6e3
	@rm -rf opengeode/*.pyc dist build *.egg-info

.PHONY: all test-parse test-ada test-llvm benchmark benchmark-O1 benchmark-O2 \
	    benchmark-O3 flake8 coverage compile-all install publish clean help
