#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This module is a free SDL editor.
    It allows to graphically design state machines, using a formal, well-
    defined language, and generate Ada code from the models.

    Opengeode also offers an API to manipulate the SDL model and diagrams
    from other Qt applications
    Example of use - to display a statechart independently from the editor
        import opengeode
        app = opengeode.init_qt() # If you don't already have a QApplication
        ast = opengeode.parse(['orchestrator.pr', 'system_structure.pr'])
        scene = opengeode.SDL_Scene('statechart')
        view = opengeode.SDL_View(scene)
        root_ast = ast[0]
        proc = root_ast.processes[0]
        opengeode.Helper.flatten(proc)
        graph = opengeode.Statechart.create_dot_graph(proc)
        opengeode.Statechart.render_statechart(scene, graph)
        view.refresh()
        view.show()
        app.exec_()
"""


from opengeode import opengeode, __version__, SDL_Scene, SDL_View, parse, init_qt
