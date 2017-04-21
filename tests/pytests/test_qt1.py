#!/usr/bin/env python
import pytest

from PySide import QtCore
from opengeode.opengeode import SDL_Scene, SDL_View
from opengeode.sdlSymbols import Label, Decision

def test_1(qtbot):
    ''' Test the parsing of numbers '''
    scene = SDL_Scene(context="process")
    scene.add_symbol(Label)
    view = SDL_View (scene)
    view.show()
    qtbot.addWidget(view)
    qtbot.keyClick(view,25)
#   assert(not isinstance(res.tree, antlr3.tree.CommonErrorNode))


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
