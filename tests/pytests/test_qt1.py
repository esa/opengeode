#!/usr/bin/env python
import pytest

from PySide import QtCore
from opengeode.opengeode import SDL_Scene, SDL_View
from opengeode.sdlSymbols import Label, Decision
from opengeode.ogParser import parser_init, floating_label
from opengeode.ogAST import Process


TEST_DATA = '''
        /* CIF label (275, 194), (70, 35) */
        connection p0:
            /* CIF decision (275, 249), (70, 50) */
            decision d;
                /* CIF ANSWER (230, 319), (70, 23) */
                (a):
                /* CIF ANSWER (320, 319), (70, 23) */
                (b):
            enddecision;
        /* CIF End Label */
        endconnection;
'''
def test_1(qtbot):
    ''' Test the parsing of numbers '''
    test   = parser_init(string=TEST_DATA)
    parsed = test.floating_label()
    ast, err, warn = floating_label(parsed.tree, parent=None, context=Process())
    scene = SDL_Scene(context="process")
    scene.render_everything(ast)
    assert (ast == None) 
    assert (len(list(scene.visible_symb))) 



if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
