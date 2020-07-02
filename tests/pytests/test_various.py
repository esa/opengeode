#!/usr/bin/env python

from opengeode.ogParser import parser_init, antlr3, sdl92Parser, lexer
from antlr3.tree import *

# return a string corresponding to a token number:
token = lambda num: lexer.tokenNamesMap[num]


def test_various_1():
    ''' Expression (should trigger error after digit 5) '''
    test = parser_init(string='''5(o)''')

    token_str = test.getTokenStream()
    res = test.expression()
    print(res.tree.toStringTree())
    # Check if there are more tokens AFTER what was parsed
    moreToken = test.getTokenStream().LT(1).start
    assert moreToken != None

def test_various_2():
    ''' Detect the syntax error '''
    test = parser_init(string=
            '''task i := 5;o ''')
    res=test.task()
    print(res.tree.toStringTree())
    # Check if there are more tokens AFTER what was parsed
    moreToken = test.getTokenStream().LT(1).start
    assert moreToken != None

if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
