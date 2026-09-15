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
export QTASTE_VERSION=2.1.1

dependencies:
	#sudo apt install -y python3 python3-pip libgl1 gnat python3-pexpect xcb libxcb-cursor0
	# installing pyside6 through pip because of bugs with QML in the Debian bullseye release
	python3 -c 'import PySide6' || python3 -m pip install pyside6
	# python3-antlr3 runtime is not available in any official repo, taking in from TASTE
	# The sdist uses an ancient ez_setup.py bootstrap that breaks on modern pip/setuptools,
	# so we download it, strip the bootstrap, and install from a local directory.
	python3 -c 'import antlr3' || (python3 -m pip install setuptools && \
	       cd /tmp && rm -rf antlr3_python3_runtime_3.4 && \
	       python3 -c "import urllib.request; urllib.request.urlretrieve('https://gitlab.esa.int/api/v4/projects/taste%2Ftaste-setup/packages/generic/dependencies/1.0/antlr3_python3_runtime_3.4.tar.bz2', 'antlr3_python3_runtime_3.4.tar.bz2')" && \
	       tar xjf antlr3_python3_runtime_3.4.tar.bz2 && \
	       cd antlr3_python3_runtime_3.4 && \
	       sed -i '/import ez_setup/d; /ez_setup.use_setuptools/d' setup.py && \
	       python3 -m pip install --no-build-isolation .)
	python3 -c 'import pygraphviz' || python3 -m pip install pygraphviz
	# install ASN1SCC in ~/.local/bin
	mkdir -p ~/.local/bin
	asn1scc -v || (cd ~/.local ; wget -q -O - https://github.com/maxime-esa/asn1scc/releases/download/4.9.0.0/asn1scc-bin-4.9.0.0.tar.bz2 | tar jxpvf - ; cd bin ; ln -sf ../asn1scc/* .)
	# install the requirement and review widget
	@echo "[-] Building Requirements and Review (optional widget)"
	# Ensure shiboken6 and shiboken6-generator versions match PySide6
	@PYSIDE_VER=$$(python3 -c "from importlib.metadata import version; v=version('PySide6'); print('.'.join(v.split('.')[:3]))") && \
	       python3 -c "from importlib.metadata import version; v=version('shiboken6'); assert '.'.join(v.split('.')[:3])=='$$PYSIDE_VER'" 2>/dev/null || \
	       python3 -m pip install shiboken6==$$PYSIDE_VER --break-system-packages && \
	       python3 -c "from importlib.metadata import version; v=version('shiboken6_generator'); assert '.'.join(v.split('.')[:3])=='$$PYSIDE_VER'" 2>/dev/null || \
	       python3 -m pip install shiboken6-generator==$$PYSIDE_VER --break-system-packages
	@python3 -c "import sys, PyTasteQtWidgets as taste, os; sys.exit(taste.__version__!=os.environ['QTASTE_VERSION'])" || \
	       (rm -rf TasteQtWidgets && \
	       git clone --depth 1 --branch ${QTASTE_VERSION} https://github.com/esa/TasteQtWidgets && \
	       cd TasteQtWidgets && \
	       sed -i 's/Py_LIMITED_API=0x03050000/Py_LIMITED_API=0x030D0000/' cmake/KDPySide6ModuleBuild.cmake && \
	       cd pytastewidgets && python3 ./install.py > /dev/null) || \
	       echo "[!] WARNING: Failed to build TasteQtWidgets (optional). Continuing without it."
	@echo [-] IMPORTANT: Make sure that ~/.local/bin is in your PATH

install: help
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

help: help/opengeode.qhc

help/opengeode.qhc:
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
