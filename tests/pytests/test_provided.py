#!/usr/bin/env python

from opengeode.ogParser import parser_init, antlr3, sdl92Parser, check_syntax

def test_1():
    ''' Test the parsing of numbers '''
    test = parser_init(string='''provided true=false; priority 5;''')
    res = test.continuous_signal()
    assert(not isinstance(res.tree, antlr3.tree.CommonErrorNode))

def test_2():
    ''' Test the parsing of numbers '''
    # Test fails without the semicolon after "true"
    test = parser_init(string='''provided true; priority 5;''')
    errCount = 0
    try:
        test.continuous_signal()
    except SyntaxError as err:
        errCount = 1
        print(f'[ERROR] {err.text}')
    assert not errCount

def test_3():
    ''' Test detection of syntax error '''
    # Test fails without the semicolon after "true"
    test = parser_init(string='''provided true; priority !;''')
    errCount = 0
    try:
        ast = test.continuous_signal()
        node = ast.tree
        check_syntax(node, node, True)
    except SyntaxError as err:
        errCount = 1
        print(f'[EXPECTED ERROR]\n {err.text}')
    assert errCount


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
