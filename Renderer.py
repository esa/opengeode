#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int

    This module is responsible for transforming AST elements to actual symbols

    It is separated from the main SDL_Scene class as the rendering can
    be done on any scene (e.g. clipboard).

    There is a single rendering function for all SDL construct, and a dispatch
    machanism (using the Python3-backported feature called singledispatch).

    Rendering can be done for single elements (returns the symbol) or for
    complete diagrams.

    This rendering capability is separated from the AST definition (ogAST.py)
    so that the AST module is kept independent from any graphical backend and
    is not related to Pyside.

    When rendering a (set of) symbol(s), update text autocompletion list(s).
"""

import ogAST
import sdlSymbols
import genericSymbols
import logging
from itertools import chain
from singledispatch import singledispatch

LOG = logging.getLogger(__name__)

__all__ = ['render']

@singledispatch
def render(ast, scene, parent, states, terminators=None):
    ''' Render a transition action symbol on the scene '''
    _, _, _, _ = scene, parent, states, terminators
    # Default behaviour is to raise an exception, if there is no
    # rendering function for a given symbol. Otherwise the dispatch
    # mechanism forwards the call to a registered function (see below)
    raise TypeError('[Renderer] Unsupported symbol in branch: ' + repr(ast))


@render.register(ogAST.Block)
def _block(ast, scene):
    ''' Render a block, containing a set of process symbols '''
    # TODO = Add text areas with signal lists, external procedures defs...
    top_level = []
    for each in ast.processes:
        top_level.append(render(each, scene))
    return top_level


@render.register(ogAST.Process)
def _process(ast, scene):
    ''' Render a Process symbol (in a BLOCK diagram) '''
    # Set autocompletion lists for input, output, state, types, variables:
    try:
        sdlSymbols.TextSymbol.completion_list = {
                t.replace('-', '_') for t in ast.dataview}
    except (AttributeError, TypeError):
        LOG.debug('No dataview for filling types autocompletion list')
    sdlSymbols.State.completion_list = {
            state for state in ast.mapping if state != 'START'}
    sdlSymbols.Input.completion_list = {
            signal['name'] for signal in ast.input_signals}
    sdlSymbols.Output.completion_list = {
            signal['name'] for signal in ast.output_signals}
    sdlSymbols.Task.completion_list = set(ast.variables.keys())

    sdlSymbols.ProcedureCall.completion_list = {
            proc.inputString for proc in ast.procedures}

    symbol = sdlSymbols.Process(ast, ast)
    scene.addItem(symbol)
    return symbol


@render.register(ogAST.Automaton)
def _automaton(ast, scene):
    ''' Render graphical elements of a process or procedure '''
    top_level_symbols = []
    # Render text areas (DCL declarations, etc.)
    for text in ast.textAreas:
        top_level_symbols.append(render(text, scene))

    # Render procedures symbols
    top_level_symbols.extend(
            [render(proc, scene)
                            for proc in ast.inner_procedures
                            if not proc.external])

    # Render the start symbol
    if ast.start:
        top_level_symbols.append(render(ast.start, scene, ast.states))

    # Render named start symbols in nested states
    for each in ast.named_start:
        top_level_symbols.append(render(each, scene, ast.states))

    # Render floating labels
    for label in ast.floating_labels:
        top_level_symbols.append(render(label, scene, ast.states))

    # Render floating states
    nested_states = []
    for state in ast.states:
        # Create only floating states
        try:
            new_state = render(state, scene=scene, states=ast.states,
                               terminators=ast.parent.terminators)
            if new_state.nested_scene:
                if str(new_state).lower() in nested_states: #.viewkeys():
                    new_state.nested_scene = None
                else:
                    nested_states.append(str(new_state).lower())
                    #nested_states[str(new_state).lower()] = \
                    #                                    new_state.nested_scene
        except TypeError:
            # Discard terminators (see _state function for explanation)
            pass
        else:
            top_level_symbols.append(new_state)
    return top_level_symbols


@render.register(ogAST.State)
def _state(ast, scene, states, terminators, parent=None):
    ''' Render a floating state and its inputs '''
    _ = parent
    # Discard the state if it is a terminator too as it is not a floating
    # state in that case: it will be rendered together with all its (possible)
    # INPUT children in the render_terminator function.
    for term in terminators:
        if(term.kind == 'next_state' and
                term.pos_x == ast.pos_x and
                term.pos_y == ast.pos_y and
                term.inputString == ast.inputString):
            raise TypeError('This state is a terminator')
    new_state = sdlSymbols.State(parent=None, ast=ast)
    if new_state not in scene.items():
        scene.addItem(new_state)

    for exit in chain(ast.inputs, ast.connects):
        render(exit, scene=scene, parent=new_state, states=states)

    new_state.nested_scene = ast.composite or ogAST.CompositeState()

    return new_state


@render.register(ogAST.Procedure)
def _procedure(ast, scene, parent=None, states=None):
    ''' Add a procedure symbol to the scene '''
    _, _ = parent, states
    proc_symbol = sdlSymbols.Procedure(ast, ast)
    scene.addItem(proc_symbol)
    return proc_symbol


@render.register(ogAST.TextArea)
def _text_area(ast, scene, parent=None, states=None):
    ''' Render a text area from the AST '''
    _, _ = parent, states
    text = sdlSymbols.TextSymbol(ast)
    scene.addItem(text)
    return text


@render.register(ogAST.Start)
def _start(ast, scene, states, parent=None):
    ''' Add the start symbol to a scene '''
    _ = parent
    start_symbol = sdlSymbols.Start(ast)
    scene.addItem(start_symbol)
    if ast.transition:
        render(ast.transition, scene=scene, parent=start_symbol, states=states)
    return start_symbol


@render.register(ogAST.CompositeState_start)
def _start(ast, scene, states, parent=None):
    ''' Add an editable start symbol to a scene (in composite states) '''
    _ = parent
    start_symbol = sdlSymbols.StateStart(ast)
    scene.addItem(start_symbol)
    if ast.transition:
        render(ast.transition,
                      scene=scene, parent=start_symbol, states=states)
    return start_symbol


@render.register(ogAST.Procedure_start)
def _procedure_start(ast, scene, states, parent=None):
    ''' Add the procedure start symbol to a scene '''
    _ = parent
    start_symbol = sdlSymbols.ProcedureStart(ast)
    scene.addItem(start_symbol)
    if ast.transition:
        render(ast.transition, scene=scene, parent=start_symbol, states=states)
    return start_symbol


@render.register(ogAST.Floating_label)
def _floating_label(ast, scene, states, parent=None):
    ''' Add a Floating label from the AST to the scene '''
    _ = parent
    lab = sdlSymbols.Label(parent=None, ast=ast)
    if lab not in scene.items():
        scene.addItem(lab)
    lab.setPos(ast.pos_x, ast.pos_y)
    if ast.transition:
        render(ast.transition, scene=scene, parent=lab, states=states)
    return lab


@render.register(ogAST.Transition)
def _transition(ast, scene, parent, states):
    ''' Add a transition to a scene '''
    for each in ast.actions:
        # pylint: disable=E1111
        parent = render(each, scene=scene, parent=parent, states=states)

    if ast.terminator:
        render(ast.terminator, scene=scene, parent=parent, states=states)


@render.register(ogAST.Comment)
def _comment(ast, scene, parent, states=None):
    ''' Create a COMMENT symbol - note: relative positionning is lost '''
    _, _ = scene, states
    return genericSymbols.Comment(parent, ast=ast)


@render.register(ogAST.Task)
def _task(ast, scene, parent, states):
    ''' Create a TASK symbol '''
    _, _ = scene, states
    return sdlSymbols.Task(parent, ast=ast)


@render.register(ogAST.Output)
def _output(ast, scene, parent, states):
    ''' Create an OUTPUT or PROCEDURE CALL symbol '''
    _, _ = scene, states
    return sdlSymbols.Output(parent, ast=ast)


@render.register(ogAST.ProcedureCall)
def _output(ast, scene, parent, states):
    ''' Create an OUTPUT or PROCEDURE CALL symbol '''
    _, _ = scene, states
    return sdlSymbols.ProcedureCall(parent, ast=ast)


@render.register(ogAST.Decision)
def _decision(ast, scene, parent, states):
    ''' Create a DECISION symbol and all its answers '''
    symbol = sdlSymbols.Decision(parent, ast=ast)
    # Place the symbol at absolute coordinates
    if not parent:
        symbol.setPos(ast.pos_x, ast.pos_y)
    for branch in ast.answers:
        render(branch,
                      scene=scene, parent=symbol, states=states)
    return symbol


@render.register(ogAST.Label)
def _label(ast, scene, parent=None, states=None):
    ''' Create a LABEL symbol '''
    _, _ = scene, states
    return sdlSymbols.Label(parent, ast=ast)


@render.register(ogAST.Answer)
def _answer(ast, scene, parent, states):
    ''' Create an ANSWER symbol and build its following transition '''
    symbol = sdlSymbols.DecisionAnswer(parent, ast=ast)
    # Place the symbol at absolute coordinates so that if
    # the branch has NEXTSTATEs symbols, they are properly placed
    if not parent:
        symbol.setPos(ast.pos_x, ast.pos_y)
    if ast.transition:
        render(ast.transition,
                      scene=scene, parent=symbol, states=states)
    return symbol


@render.register(ogAST.Terminator)
def _terminator(ast, scene, parent, states):
    ''' Create a TERMINATOR symbol '''
    if ast.label:
        # pylint: disable=E1111
        parent = render(ast.label,scene=scene, parent=parent, states=states)
    if ast.kind == 'next_state':
        LOG.debug('ADDING NEXT_STATE ' + ast.inputString)
        # Create a new state symbol
        symbol = sdlSymbols.State(parent=parent, ast=ast)
        # If the terminator is also a new state, render the inputs below
        LOG.debug('STATELIST:' + str([st.inputString for st in states]))
        for state_ast in states:
            if (state_ast.inputString == ast.inputString and
                    state_ast.pos_x == ast.pos_x and
                    state_ast.pos_y == ast.pos_y):
                LOG.debug('MERGING TERMINATOR "' + ast.inputString + '"')
                symbol.nested_scene = state_ast.composite or \
                                      ogAST.CompositeState()
                for each in chain(state_ast.inputs, state_ast.connects):
                    render(each, scene=scene, parent=symbol, states=states)
                break
    elif ast.kind == 'join':
        symbol = sdlSymbols.Join(parent, ast)
    elif ast.kind in ('return', 'stop'):
        symbol = sdlSymbols.ProcedureStop(parent, ast)
    else:
        raise TypeError('Unsupported terminator: ' + repr(ast))
    return symbol


@render.register(ogAST.Input)
def _input(ast, scene, parent, states):
    ''' Add input from the AST to the scene '''
    # Note: PROVIDED clause is not supported
    inp = sdlSymbols.Input(parent, ast=ast)
    if inp not in scene.items():
        scene.addItem(inp)
    if not parent:
        inp.setPos(ast.pos_x, ast.pos_y)
    if ast.transition:
        render(ast.transition,
               scene=scene,
               parent=inp,
               states=states)
    return inp

@render.register(ogAST.Connect)
def _connect(ast, scene, parent, states):
    ''' Add connect symbol from the AST to the scene '''
    conn = sdlSymbols.Connect(parent, ast=ast)
    if conn not in scene.items():
        scene.addItem(conn)
    if not parent:
        conn.setPos(ast.pos_x, ast.pos_y)
    if ast.transition:
        render(ast.transition,
               scene=scene,
               parent=conn,
               states=states)
    return conn
