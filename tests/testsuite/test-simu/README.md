run make simu
this will build the property files but not include them for execution with the simulator

until this is fixed, you must stop the simulator, and then copy these files:

properties
liborchestrator_stop_conditions.o

into the orchestrator_simu folder

and then go in that folder and run:

opengeode-simulator -p properties

EDIT: the SDL-only simulator code is not generated anymore in favour of the
TASTE simulator engine which allows to run more than one SDL model at a time.
This save a lot of code in the Ada backend making it easier to maintain.

