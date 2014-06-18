
rem This batch is used to compile SDL92 grammar using antlr runtime

set CLASSPATH=./antlr-3.1.3/lib/antlr-3.1.3.jar
java org.antlr.Tool sdl92.g 
pause