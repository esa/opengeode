all:
	gnatmake -d -P GPS_project.gpr mainprogram.adb --subdirs=debug -cargs -g -O0
	touch builtWithoutCoverage
	
coverage:
	if [ -f builtWithoutCoverage ] ; then make clean ; fi
	gnatmake -d -P GPS_project.gpr mainprogram.adb --subdirs=debug -cargs -g -O0 -fprofile-arcs -ftest-coverage -largs -fprofile-arcs
	cd bin/debug ; ./mainprogram
	cd bin/debug ; gcov adaasn1rtl taste_dataview taste_basictypes
	
clean:
	rm -f builtWithoutCoverage ;
	gnat clean -r -P GPS_project.gpr --subdirs=debug	