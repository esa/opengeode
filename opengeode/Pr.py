#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates textual SDL code (PR format)
    by parsing the graphical symbols.

    Copyright (c) 2012-2022 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from collections import deque
from itertools import chain
from functools import singledispatch

from . import genericSymbols, sdlSymbols, Connectors

LOG = logging.getLogger(__name__)

__all__ = ['parse_scene', 'generate']

g_useSymbolId = False

class Indent(deque):
    ''' Extension of the deque class to support automatic indentation '''
    indent = 0

    def append(self, string):
        ''' Redefinition of the append to insert the indent pattern '''
        super().append('    ' * Indent.indent + string)


def parse_scene(scene, full_model=False, use_symbol_id=False):
    ''' Return the PR string for a complete scene
        Optionally, also generate the SYSTEM structure, with channels, etc. '''
    global g_useSymbolId
    # Decide to use the symbol ID rather than the CIF coordinates
    g_useSymbolId = use_symbol_id
    pr_data = Indent()
    if full_model:
        # Generate a complete SDL system - to have everything in a single file
        # (1) get system name
        # (2) get signal directions from the connection of the process to env
        # (3) generate all the text
        processes = list(scene.processes)
        system_name = 'sys'
        block_name = 'block1'
        ast_obj = getattr(scene, 'ast', None)
        if ast_obj is not None:
            if ast_obj.__class__.__name__ == 'Block':
                block_name = ast_obj.name or 'block1'
                if getattr(ast_obj, 'parent', None) is not None:
                    system_name = ast_obj.parent.name or 'sys'
            elif getattr(ast_obj, 'systems', None):
                try:
                    system = ast_obj.systems[0]
                    system_name = system.name or 'sys'
                    if system.blocks:
                        block_name = system.blocks[0].name or 'block1'
                except (IndexError, AttributeError):
                    pass
        else:
            system_name = str(processes[0]) if processes else 'OpenGEODE'
            block_name = system_name

        pr_data.append('system {};'.format(system_name))
        Indent.indent = 1
        pr_data.append('signal dummy;')
        channels, routes = Indent(), Indent()
        for each in scene.texts:
            # Parse text areas to retrieve signal names USELESS
           pr = generate(each)
           pr_data.extend(pr)
        # Get all Signalroute and Channel connections in the scene
        all_connections = [item for item in scene.items() if isinstance(item, Connectors.Signalroute)]

        channel_idx = 1
        route_idx = 1
        for conn in all_connections:
            if isinstance(conn, Connectors.Channel):
                # Channel between two processes (only generated at block level as signalroute)
                Indent.indent = 2
                routes.append(f'signalroute r{route_idx}')
                Indent.indent += 1
                out_sig = conn.out_sig or 'dummy'
                in_sig = conn.in_sig or 'dummy'
                routes.append(f'from {str(conn.parent)} to {str(conn.child)} with {out_sig};')
                routes.append(f'from {str(conn.child)} to {str(conn.parent)} with {in_sig};')
                Indent.indent = 1
                route_idx += 1
            else:
                # Signalroute to environment
                to_env = conn.out_sig or 'dummy'
                from_env = conn.in_sig or 'dummy'
                chan_name = f'c{channel_idx}'
                rout_name = f'r{route_idx}'
                
                Indent.indent = 1
                channels.append(f'channel {chan_name}')
                Indent.indent += 1
                channels.append(f'from env to {block_name} with {from_env};')
                channels.append(f'from {block_name} to env with {to_env};')
                Indent.indent -= 1
                channels.append('endchannel;')
                
                Indent.indent = 2
                routes.append(f'signalroute {rout_name}')
                Indent.indent += 1
                routes.append(f'from env to {str(conn.parent)} with {from_env};')
                routes.append(f'from {str(conn.parent)} to env with {to_env};')
                Indent.indent -= 1
                routes.append(f'connect {chan_name} and {rout_name};')
                Indent.indent = 1
                
                channel_idx += 1
                route_idx += 1

        pr_data.extend(channels)
        pr_data.append('block {};'.format(block_name))
        Indent.indent = 2
        pr_data.extend(routes)
        for each in processes:
            pr_data.extend(generate(each))
        Indent.indent -= 1
        pr_data.append('endblock;')
        Indent.indent -= 1
        pr_data.append('endsystem;')

    else:
        for each in scene.processes:
            if ":" in str(each):
                # ignore instances of process type
                continue
            #pr_data.extend(generate(each))
            # Only one process is supported - return now because
            # the text areas must not be parsed - some may have been
            # generated automatically to display the list of signals
            # and external procedures when interface was generated by TASTE
            return list(generate(each))

        # The scene may be split into partitions, but for PR generation
        # everything is at the same level -> gather everything, it is
        # important to respect the ordering of things in the output
        # (the start and declarations must be generated first)
        texts, procs, start, floating_labels, states, composite_states = \
                [], [], [], [], [], dict()

        if scene.context == 'process':
            partitions = scene.partitions.values() if getattr(scene, 'partitions', None) else [scene]
            for part in partitions:

                # this includes the current scene
                texts.extend(part.texts)
                procs.extend(part.procs)
                start.extend(part.start)
                floating_labels.extend(part.floating_labels)
                states.extend(part.states)
                composite_states.update(part.composite_states)
        else:
                texts = scene.texts
                procs = scene.procs
                start = scene.start
                floating_labels = scene.floating_labels
                states = scene.states
                composite_states = scene.composite_states

        for each in chain(texts, procs, start):
            pr_data.extend(generate(each))
        for each in floating_labels:
            pr_data.extend(generate(each))
        composite = set(composite_states.keys())
        for each in states:
            if each.is_composite():
                # Ignore via clause:
                statename = str(each).split()[0].lower()
                try:
                    composite.remove(statename)
                    sub_state = generate(each, composite=True, nextstate=False)
                    if sub_state:
                        sub_state.reverse()
                        pr_data.extendleft(sub_state)
                except KeyError:
                    pass
            pr_data.extend(generate(each, nextstate=False))
    return list(pr_data)


def cif_coord(name, symbol):
    ''' PR string for the CIF coordinates/size of a symbol '''
    cif1 = '/* CIF {symb} ({x}, {y}), ({w}, {h}) */'.format(
            symb=name,
            x=int(symbol.scenePos().x()), y=int(symbol.scenePos().y()),
            w=int(symbol.boundingRect().width()),
            h=int(symbol.boundingRect().height()))
    cif2 = '' if not g_useSymbolId else f'\n{cif_symbolid(symbol)}'
    return cif1+cif2

def cif_symbolid(symbol):
    ''' CIF string returning the Python's identifier of a symbol, used only
    when parsing an already rendered diagram. This allows to keep the link
    between the re-parsed AST and the existing symbols, that is useful when
    reporting errors '''
    return f'/* CIF _id {id(symbol)} */'


def hyperlink(symbol):
    ''' PR string for the optional hyperlink associated to a symbol '''
    return f"/* CIF Keep Specific Geode HyperLink '{symbol.text.hyperlink}' */"


def req_server(symbol):
    ''' Gitlab server holding requirements '''
    if genericSymbols.g_QtTaste:
        url = genericSymbols.g_url
        if type(url) != str:
            url = url.toString()
        return f"/* CIF Keep Specific Geode _REQSERVER_ '{url}' */"
    else:
        return ''

def req_ids(symbol):
    ''' PR string for the optional requirement ids associated to a symbol '''
    ticked = symbol.ast.req_ids
    if symbol.req_model is not None:
        # User has opened the requirement manager, take the list from there
        # (some requirements may have been unselected)
        ticked = symbol.req_model.selectedRequirements()
    #selected=set(ticked)
    result = []
    for each in ticked:
        result.append(f"/* CIF Keep Specific Geode _REQID_ '{each}' */")
    return result


def rid_ids(symbol):
    ''' PR string for the optional requirement ids associated to a symbol '''
    # Check if some RIDs apply to this symbol and save their IDs
    rids = symbol.ast.rid_ids
    result = []
    for each in rids:
        result.append(f"/* CIF Keep Specific Geode _RIDID_ '{each}' */")
    return result


def partition(symbol):
    scene = symbol.scene()
    if scene:
        part_name = scene.partition_name
        return f"/* CIF Keep Specific Geode Partition '{part_name}' */"
    else:
        return ''


def common(name, symbol):
    ''' PR string format that is shared by most symbols '''
    result = Indent()
    result.append(cif_coord(name, symbol))
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    if isinstance(symbol, (sdlSymbols.State, sdlSymbols.Procedure)) and name != 'NEXTSTATE':
        part = partition(symbol)
        if part:
            result.append(part)
    result.append('{} {}{}'.format(name, str(symbol.text), ';'
                               if not symbol.comment else ''))
    if symbol.comment:
        result.extend(generate(symbol.comment))
    return result


def recursive_aligned(symbol):
    ''' Get the branch following symbol '''
    result = Indent()
    Indent.indent += 1
    next_symbol = symbol.next_aligned_symbol()
    while next_symbol:
        result.extend(generate(next_symbol))
        next_symbol = next_symbol.next_aligned_symbol()
    Indent.indent -= 1
    return result


@singledispatch
def generate(symbol, *args, **kwargs):
    ''' Generate text for a symbol, recursively or not - return a list of
        strings '''
    _ = symbol
    raise NotImplementedError('Unsupported AST construct: {}'
                              .format(type(symbol)))
    return Indent()


@generate.register(genericSymbols.Comment)
def _comment(symbol, **kwargs):
    ''' Optional comment linked to a symbol '''
    result = Indent()
    result.append(cif_coord('comment', symbol))
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append("comment '" + str(symbol.text).replace("'", "\\'") + "';")
    return result


@generate.register(sdlSymbols.Input)
def _input(symbol, recursive=True, **kwargs):
    ''' Input symbol or branch if recursive is set '''
    result = common('input', symbol)
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.ContinuousSignal)
def _continuous_signal(symbol, recursive=True, **kwargs):
    ''' "Provided" symbol or branch if recursive is set '''
    result = common('provided', symbol)
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Connect)
def _connect(symbol, recursive=True, **kwargs):
    ''' Connect symbol or branch if recursive is set '''
    result = common('connect', symbol)
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Output)
def _output(symbol, **kwargs):
    ''' Output symbol '''
    return common('output', symbol)


@generate.register(sdlSymbols.Decision)
@generate.register(sdlSymbols.Alternative)
def _decision(symbol, recursive=True, **kwargs):
    ''' Decision symbol or branch if recursive is set '''
    startname = 'alternative' if isinstance(symbol, sdlSymbols.Alternative) \
            else 'decision'
    endname = 'endalternative' if isinstance(symbol, sdlSymbols.Alternative) \
            else 'enddecision'
    result = common(startname, symbol)
    if recursive:
        else_branch = None
        Indent.indent += 1
        for answer in symbol.branches():
            if str(answer).lower().strip() == 'else':
                else_branch = generate(answer)
            else:
                result.extend(generate(answer))
        if else_branch:
            result.extend(else_branch)
        Indent.indent -= 1
    result.append(f'{endname};')
    return result


@generate.register(sdlSymbols.DecisionAnswer)
def _decisionanswer(symbol, recursive=True, **kwargs):
    ''' Decision Answer symbol or branch if recursive is set '''
    result = Indent()
    result.append(cif_coord('ANSWER', symbol))
    ans = str(symbol)
    if ans.lower().strip() != 'else':
        ans = f'({ans})'
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append(f'{ans}:')
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Join)
def _join(symbol, **kwargs):
    ''' Join symbol '''
    return common('join', symbol)


@generate.register(sdlSymbols.ProcedureStop)
def _procedurestop(symbol, **kwargs):
    ''' Procedure Stop symbol '''
    return common('return', symbol)


@generate.register(sdlSymbols.ProcessStop)
def _processstop(symbol, **kwargs):
    ''' Process Stop symbol '''
    result = Indent()
    result.append(cif_coord('stop', symbol))
    result.append('stop' + ';' if not symbol.comment else '')
    if symbol.comment:
        result.extend(generate(symbol.comment))
    return result

@generate.register(sdlSymbols.Task)
def _task(symbol, **kwargs):
    ''' Task symbol '''
    return common('task', symbol)


@generate.register(sdlSymbols.ProcedureCall)
def _procedurecall(symbol, **kwargs):
    ''' Procedure call symbol '''
    result = Indent()
    result.append(cif_coord('PROCEDURECALL', symbol))
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append('call {}{}'.format(str(symbol.text), ';'
                                      if not symbol.comment else ''))
    if symbol.comment:
        result.extend(generate(symbol.comment))
    return result


@generate.register(sdlSymbols.Create)
def _procedurecall(symbol, **kwargs):
    ''' CREATE symbol '''
    result = Indent()
    result.append(cif_coord('CREATE', symbol))
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append(f'create {str(symbol.text)}{";" if not symbol.comment else ""}')
    if symbol.comment:
        result.extend(generate(symbol.comment))
    return result


@generate.register(sdlSymbols.TextSymbol)
def _textsymbol(symbol, **kwargs):
    ''' Text Area symbol '''
    result = Indent()
    #if symbol.text.hyperlink:
    # no hyperlink for text symbols (see sdl92.g)
    #    result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    part = partition(symbol)
    if part:
        result.append(part)
    result.append(cif_coord('TEXT', symbol))
    # Align nicely the text (parser will dedent it)
    for line in str(symbol.text).split('\n'):
        result.append(line)
    result.append('/* CIF ENDTEXT */')
    return result


@generate.register(sdlSymbols.Label)
def _label(symbol, recursive=True, **kwargs):
    ''' Label symbol or branch if recursive is set '''
    result = Indent()
    result.append(cif_coord('label', symbol))
    if symbol.text.hyperlink:
        result.append(hyperlink(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    if symbol.common_name == 'floating_label':
        part = partition(symbol)
        if part:
            result.append(part)
        result.append(f'connection {str(symbol)}:')
        if recursive:
            result.extend(recursive_aligned(symbol))
        result.append('/* CIF End Label */')
        result.append('endconnection;')
    else:
        result.append(f'{str(symbol)}:')
    return result


@generate.register(sdlSymbols.State)
def _state(symbol, recursive=True, nextstate=True, composite=False, cpy=False,
           **kwargs):
    ''' State/Nextstate symbol or branch if recursive is set '''
    if nextstate and symbol.hasParent:
        result = common('NEXTSTATE', symbol)
    elif not composite and symbol.hasParent and not cpy \
            and not [each for each in symbol.childSymbols()
            if not isinstance(each, genericSymbols.Comment)]:
        # If nextstate has no child, don't generate anything
        result = []
    elif not composite:
        result = common('state', symbol)
        if recursive:
            Indent.indent += 1
            # Generate code for INPUT and CONNECT symbols
            for each in (symb for symb in symbol.childSymbols()
                         if isinstance(symb, (sdlSymbols.Input,
                                              sdlSymbols.ContinuousSignal))):
                result.extend(generate(each))
            Indent.indent -= 1
        result.append('endstate;')
    else:
        # Generate code for a nested state
        result = Indent()
        agg = ' aggregation' if symbol.nested_scene.is_aggregation() else ''#if not list(symbol.nested_scene.start) else ''
        result.append('state{} {};'.format(agg, str(symbol).split()[0]))
        result.append('substructure')
        Indent.indent += 1
        entry_points, exit_points = [], []
        for each in symbol.nested_scene.start:
            if str(each):
                entry_points.append(str(each))
        for each in symbol.nested_scene.returns:
            if str(each) != 'no_name':
                exit_points.append(str(each))
        if entry_points:
            result.append('in ({});'.format(','.join(entry_points)))
        if exit_points:
            result.append('out ({});'.format(','.join(exit_points)))
        Indent.indent += 1
        result.extend(parse_scene(symbol.nested_scene, use_symbol_id=g_useSymbolId))
        Indent.indent -= 1
        Indent.indent -= 1
        result.append('endsubstructure;')
    return result


@generate.register(sdlSymbols.Process)
@generate.register(sdlSymbols.ProcessType)
def _process(symbol, recursive=True, **kwargs):
    ''' Process symbol and inner content if recursive is set '''
    name = "process type" if isinstance(symbol, sdlSymbols.ProcessType) \
            else "process"
    #result = common(name, symbol)
    result = Indent()
    result.append(cif_coord('PROCESS', symbol))
    result.append(req_server(symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append("{} {}{}".format(name, str(symbol.text), ";" if
        not symbol.comment else ""))
    if symbol.comment:
        result.extend(generate(symbol.comment))

    if recursive and symbol.nested_scene:
        Indent.indent += 1
        nested = symbol.nested_scene
        result.extend(parse_scene(nested, use_symbol_id=g_useSymbolId))
        Indent.indent -= 1
    if ":" not in str(symbol):
        result.append('endprocess {}{};'
                .format("type " if isinstance(symbol, sdlSymbols.ProcessType)
                                else "",
                        str(symbol)))
    return result


@generate.register(sdlSymbols.Procedure)
def _procedure(symbol, recursive=True, **kwargs):
    ''' Procedure symbol or branch if recursive is set '''
    result = common('procedure', symbol)
    if recursive and symbol.nested_scene:
        Indent.indent += 1
        result.extend(parse_scene(symbol.nested_scene, use_symbol_id=g_useSymbolId))
        Indent.indent -= 1
    result.append('endprocedure;')
    return result


@generate.register(sdlSymbols.Start)
def _start(symbol, recursive=True, **kwargs):
    ''' START symbol or branch if recursive is set '''
    result = Indent()
    result.append(cif_coord('START', symbol))
    result.extend(req_ids(symbol))
    result.extend(rid_ids(symbol))
    result.append('START{via}{comment}'
                  .format(via=(' ' + str(symbol) + ' ')
                          if str(symbol).replace('START', '') else '',
                          comment=';' if not symbol.comment else ''))
    if symbol.comment:
        result.extend(generate(symbol.comment))
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(Connectors.Signalroute)
def _channel(symbol, recursive=True, **kwargs):
    ''' Signalroute at block level '''
    result = Indent()
    result.append('signalroute c')
    Indent.indent += 1
    if isinstance(symbol, Connectors.Channel):
        out_sig = symbol.out_sig or 'dummy'
        in_sig = symbol.in_sig or 'dummy'
        result.append('from {} to {} with {};'.format(str(symbol.parent),
                                                       str(symbol.child),
                                                       out_sig))
        result.append('from {} to {} with {};'.format(str(symbol.child),
                                                       str(symbol.parent),
                                                       in_sig))
    else:
        out_sig = symbol.out_sig or 'dummy'
        in_sig = symbol.in_sig or 'dummy'
        result.append('from {} to env with {};'.format(str(symbol.parent),
                                                       out_sig))
        result.append('from env to {} with {};'.format(str(symbol.parent),
                                                       in_sig))
    Indent.indent -= 1
    return result



