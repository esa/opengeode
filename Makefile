all: compile-all

regression:
	make -C tests/regression all

coverage: 
	make -C tests/regression coverage

compile-all:
	pyside-rcc opengeode.qrc -o icons.py
	if [ ! -f antlr-3.1.3.tar.bz2 ]; then wget http://download.tuxfamily.org/taste/misc/antlr-3.1.3.tar.bz2 ; tar jxvf antlr-3.1.3.tar.bz2 ; fi
	CLASSPATH=$$PWD/antlr-3.1.3/lib/antlr-3.1.3.jar java org.antlr.Tool sdl92.g

install: compile-all
	mkdir -p opengeode
	for f in AdaGenerator.py __init__.py genericSymbols.py icons.py ogAST.py ogParser.py opengeode.py Renderer.py samnmax.py sdl92Lexer.py sdl92Parser.py sdlSymbols.py undoCommands.py Clipboard.py Statechart.py LlvmGenerator.py Lander.py Helper.py Connectors.py; do echo Installing $$f && cp $$f opengeode; done
	python setup.py install

publish: install
	python setup.py sdist upload

clean:
	find . -name '*~' | xargs rm -f
	find . -name '*.o' | xargs rm -f
