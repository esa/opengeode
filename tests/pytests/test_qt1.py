#!/usr/bin/env python
import pytest

from PySide import QtCore
from opengeode.opengeode import SDL_Scene, SDL_View, G_SYMBOLS
from opengeode.sdlSymbols import Label, Decision
from opengeode.ogParser import parseSingleElement
from opengeode.ogAST import Process, Automaton


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
    ast = Automaton()
    floating, _, _, _, _ = parseSingleElement('floating_label', TEST_DATA)
    ast.floating_labels = [floating]
    ast.parent = Process()
    scene = SDL_Scene(context="process")
    scene.render_everything(ast)
    assert (len(list(scene.floating_symb)) == 1)



if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
