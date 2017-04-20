#!/usr/bin/env python

from opengeode.opengeode import SDL_Scene
from opengeode.sdlSymbols import Label, Decision

def test_1(qtbot):
    ''' Test the parsing of numbers '''
    scene = SDL_Scene(context="process")
    qtbot.addWidget(scene)
    scene.add_symbol(Label)
#   test = parser_init(string='''provided true=false; priority 5;''')
#   res = test.continuous_signal()
#   assert(not isinstance(res.tree, antlr3.tree.CommonErrorNode))


if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
