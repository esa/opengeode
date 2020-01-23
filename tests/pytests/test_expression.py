#!/usr/bin/env python

from opengeode.ogParser import parser_init, antlr3, sdl92Parser


def test_minus():
    ''' Test the parsing of numbers '''
    test = parser_init(string='''1-1''')
    test.expression()


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
