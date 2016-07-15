#!/usr/bin/env python

from opengeode.ogParser import parser_init, antlr3, sdl92Parser, samnmax

# return a string corresponding to a token number:
token = lambda num: sdl92Parser.tokenNames[num]

def test_1():
    ''' Test the parsing of numbers '''
    test = parser_init(string='''provided true=false; priority 5;''')
    res = test.continuous_signal()
    assert(not isinstance(res.tree, antlr3.tree.CommonErrorNode))

def test_2():
    ''' Test the parsing of numbers '''
    test = parser_init(string='''provided true priority 5;''')
    with samnmax.capture_output() as (stdout, stderr):
        test.continuous_signal()
    errCount = 0
    for each in stderr:
        print('[ERROR] ' + str(each))
        errCount += 1
    assert not errCount


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
