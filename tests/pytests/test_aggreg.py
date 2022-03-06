#!/usr/bin/env python3

from opengeode.ogParser import parser_init, antlr3, sdl92Parser, lexer

# return a string corresponding to a token number:
token = lambda num: lexer.tokenNamesMap[num]


def test_composite_state_body_1():
    ''' Detect the syntax error (missing SEMI after "procedure entry") '''
    test = parser_init(string=
    '''state ENTRYA;
       substructure
           procedure entry external;
       endsubstructure ENTRYA;''')
    # Parse and then check that the reported error is the expected one

    res = test.composite_state_body()
    assert(not isinstance(res.tree, antlr3.tree.CommonErrorNode))
    composite = res.tree.children[0]
    compo_type = token(composite.type)
    assert(compo_type == 'COMPOSITE_STATE')
    for each in composite.children:
        if isinstance(each, antlr3.tree.CommonErrorNode):
            exception = each.trappedException
            assert(isinstance(exception,antlr3.NoViableAltException))
            assert(token(exception.unexpectedType) == 'EXTERNAL')


def test_composite_state_1():
    ''' Detect the syntax error (missing SEMI after "procedure entry") '''
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


def test_composite_state_body_2():
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
    for name, value in dict(globals()).items():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
