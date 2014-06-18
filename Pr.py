#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates textual SDL code (PR format)
    by parsing the graphical symbols.

    Copyright (c) 2012-2014 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from singledispatch import singledispatch

import genericSymbols, sdlSymbols

LOG = logging.getLogger(__name__)

__all__ = ['generate']


def cif_coord(name, symbol):
    ''' PR string for the CIF coordinates/size of a symbol '''
    return u'/* CIF {symb} ({x}, {y}), ({w}, {h}) */'.format(
            symb=name,
            x=int(symbol.scenePos().x()), y=int(symbol.scenePos().y()),
            w=int(symbol.boundingRect().width()),
            h=int(symbol.boundingRect().height()))


def hyperlink(symbol):
    ''' PR string for the optional hyperlink associated to a symbol '''
    return u"/* CIF Keep Specific Geode HyperLink '{}' */".format(
                                                              symbol.hyperlink)


def common(name, symbol):
    ''' PR string format that is shared by most symbols '''
    result = [cif_coord(name, symbol)]
    if symbol.hyperlink:
        result.append(hyperlink(symbol))
    result.append(u'{} {}{}'.format(name, unicode(symbol.text), ';'
                                if not symbol.comment else ''))
    if symbol.comment:
        result.extend(generate(symbol.comment))
    return result


def recursive_aligned(symbol):
    ''' Get the branch following symbol '''
    result = []
    next_symbol = symbol.next_aligned_symbol()
    while next_symbol:
        result.extend(generate(next_symbol))
        next_symbol = next_symbol.next_aligned_symbol()
    return result


@singledispatch
def generate(symbol, recursive=True):
    ''' Generate text for a symbol, recursively or not - return a list of
        strings '''
    _, _ = symbol, recursive
    raise NotImplementedError('[PR Generator] Unsupported AST construct')
    return []


@generate.register(genericSymbols.Comment)
def _comment(symbol):
    ''' Optional comment linked to a symbol '''
    result = [cif_coord('COMMENT', symbol)]
    if symbol.hyperlink:
        result.append(hyperlink(symbol))
    result.append('COMMENT \'{}\';'.format(unicode(symbol.text)))
    return result


@generate.register(sdlSymbols.Input)
def _input(symbol, recursive=True):
    ''' Input symbol or branch if recursive is set '''
    result = common('INPUT', symbol)
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Connect)
def _connect(symbol, recursive=True):
    ''' Connect symbol or branch if recursive is set '''
    result = common('CONNECT', symbol)
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Output)
def _output(symbol):
    ''' Output symbol '''
    return common('OUTPUT', symbol)


@generate.register(sdlSymbols.Decision)
def _decision(symbol, recursive=True):
    ''' Decision symbol or branch if recursive is set '''
    result = common('DECISION', symbol)
    if recursive:
        else_branch = None
        for answer in symbol.branches():
            if unicode(answer).lower().strip() == 'else':
                else_branch = generate(answer)
            else:
                result.extend(generate(answer))
        if else_branch:
            result.extend(else_branch)
    result.append('ENDDECISION;')


@generate.register(sdlSymbols.DecisionAnswer)
def _decisionanswer(symbol, recursive=True):
    ''' Decision Answer symbol or branch if recursive is set '''
    ans = unicode(symbol)
    if ans.lower().strip() != u'else':
        ans = u'({})'.format(ans)
    result = [cif_coord('ANSWER', symbol)]
    if symbol.hyperlink:
        result.append(hyperlink(symbol))
    result.append('{}:'.format(ans))
    if recursive:
        result.extend(recursive_aligned(symbol))
    return result


@generate.register(sdlSymbols.Join)
def _join(symbol):
    ''' Join symbol '''
    return common('JOIN', symbol)


@generate.register(sdlSymbols.ProcedureStop)
def _procedurestop(symbol):
    ''' Procedure Stop symbol '''
    return common('RETURN', symbol)


@generate.register(sdlSymbols.Label)
def _label(symbol, recursive=True):
    ''' Label symbol or branch if recursive is set '''
    _, _ = symbol, recursive


@generate.register(sdlSymbols.Task)
def _task(symbol):
    ''' Task symbol '''
    return common('TASK', symbol)


@generate.register(sdlSymbols.ProcedureCall)
def _procedurecall(symbol):
    ''' Procedure call symbol '''
    result = [cif_coord('PROCEDURECALL', symbol)]
    if symbol.hyperlink:
        result.append(hyperlink(symbol))
    result.append(u'CALL {}{}'.format(unicode(symbol.text), ';'
                                      if not symbol.comment else ''))
    return result


@generate.register(sdlSymbols.TextSymbol)
def _textsymbol(symbol):
    ''' Text Area symbol '''
    result = [cif_coord('TEXT', symbol)]
    if symbol.hyperlink:
        result.append(hyperlink(symbol))
    result.append(unicode(symbol.text))
    result.append('/* CIF ENDTEXT */')
    return result


@generate.register(sdlSymbols.State)
def _state(symbol, recursive=True):
    ''' State symbol or branch if recursive is set '''
    _, _ = symbol, recursive


@generate.register(sdlSymbols.Process)
def _process(symbol, recursive=True):
    ''' Process symbol or branch if recursive is set '''
    _, _ = symbol, recursive


@generate.register(sdlSymbols.Procedure)
def _procedure(symbol, recursive=True):
    ''' Procedure symbol or branch if recursive is set '''
    _, _ = symbol, recursive


@generate.register(sdlSymbols.Start)
def _start(symbol, recursive=True):
    ''' START symbol or branch if recursive is set '''
    _, _ = symbol, recursive
