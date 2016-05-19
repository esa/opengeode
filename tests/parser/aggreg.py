#!/usr/bin/env python

from opengeode.ogParser import parser_init

# detect syntax errors (missing semi after "entry")

def test_composite_state_body_1():

    test = parser_init(string=
    '''state ENTRYA;
              substructure
                procedure entry EXTERNAL;
              endsubstructure ENTRYA;
    ''')
    test.composite_state_body()


def test_composite_state_1():
    test = parser_init(string=
    '''state CHECKING;
            substructure
              state ENTRYA;
              substructure
                procedure entry EXTERNAL;
              endsubstructure ENTRYA;
            endsubstructure CHECKING;
    ''')

    test.composite_state()


def test_composite_state_2():
    print('composite_state (should have no error)')

    test=parser_init(string=
    '''state CHECKING;
            substructure
              state ENTRYA;
              endstate ENTRYA;
            endsubstructure CHECKING;
    ''')

    test.composite_state()


def test_composite_state_body_1():
    print('composite_state_body 2:')

    test=parser_init(string=
    '''state ENTRYA;
              endstate;
    ''')

    test.composite_state_body()


def test_composite_state_3():
    print('from rm - reports that start must be before state:')
    test=parser_init(string=
    '''
    STATE AGGREGATION DemoDeviceDACPStates;
            SUBSTRUCTURE
              STATE INTERNAL_MAPPINGS;
                SUBSTRUCTURE
                  STATE STATELESS;
                  ENDSTATE STATELESS;
                  START;
                  NEXTSTATE STATELESS;
                ENDSUBSTRUCTURE INTERNAL_MAPPINGS;
            ENDSUBSTRUCTURE DemoDeviceDACPStates;
    ''')

    test.composite_state()


def test_composite_state_4():
    print('from rm(2) - reports that start must be before state:')
    test=parser_init(string=
    '''
    process hello;
    STATE AGGREGATION DemoDeviceDACPStates;
            SUBSTRUCTURE
              STATE INTERNAL_MAPPINGS;
                SUBSTRUCTURE
                  STATE STATELESS;
                  ENDSTATE STATELESS;
                  START;
                  NEXTSTATE STATELESS;
                ENDSUBSTRUCTURE INTERNAL_MAPPINGS;
            ENDSUBSTRUCTURE DemoDeviceDACPStates;
    end hello;
    ''')

    test.process_definition()


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
