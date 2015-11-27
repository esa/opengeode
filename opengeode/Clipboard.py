#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int

    This module is managing the Copy and Paste functions.
"""

import traceback
import logging
from itertools import chain
import PySide

import ogAST
import sdlSymbols
import genericSymbols
import Renderer
import Pr

__all__ = ['copy', 'paste']

LOG = logging.getLogger(__name__)

# Buffer holding the list of copied symbols in AST form
COPY_PASTE = []

# Actual scene clipboard
CLIPBOARD = None


def copy(selection):
    ''' Create a copy (duplicate) of the selected symbols in AST form '''
    # Clear the copy paste buffer
    COPY_PASTE[:] = []
    branch_top_level = []
    floating_items = []
    for item in selection:
        # When several items are selected, take the first of each subbranch
        if item.hasParent and not item.parentItem().grabber.isSelected():
            branch_top_level.append(item)
        elif not item.hasParent:
            # Take also floating items
            floating_items.append(item)
    # Check if selected items would allow a paste - reject copy otherwise
    # e.g. floating and non-floating items cannot be pasted together
    if ((branch_top_level == []) == (floating_items == []) or
            len(branch_top_level) > 1):
        raise TypeError('Selection is incompatible with copy')
    # Then parse/copy the selected branches
    for item in branch_top_level + floating_items:
        branch_ast, terminators = copy_branch(item)
        COPY_PASTE.append((branch_ast, terminators))
    LOG.debug('COPY-PASTE LIST:' + str(COPY_PASTE))


def copy_branch(top_level_item):
    ''' Copy branches (recursively) '''
    res_terminators = []
    pr_text = '\n'.join(Pr.generate(top_level_item, cpy=True,
                                    nextstate=False, recursive=True))
    item_ast, terminators = top_level_item.get_ast(pr_text)
    LOG.debug('COPY ' + str(item_ast))
    if not item_ast:
        LOG.error('ERROR - copy failed')
        return

    branch = [item_ast]

    # If top_level_item is an horizontal symbol, all its children (branch)
    # are automatically copied. In the case that several following symbols
    # are selected however, the followers of the top_level must be
    # explicitely added to the copy list:
    if not isinstance(top_level_item, genericSymbols.HorizontalSymbol):
        next_aligned = top_level_item.next_aligned_symbol()
        while next_aligned and next_aligned.grabber.isSelected():
            pr_text = '\n'.join(Pr.generate(next_aligned, cpy=True,
                                            nextstate=False, recursive=True))
            next_ast, next_terminators = next_aligned.get_ast(pr_text)
            terminators.extend(next_terminators)
            branch.append(next_ast)
            next_aligned = next_aligned.next_aligned_symbol()

    # Parse terminators recursively (e.g. NEXTSTATE)
    res_terminators = terminators
    for term in terminators:
        # Get symbol at terminator coordinates
        symbols = top_level_item.scene().items(PySide.QtCore.QRectF
                (term.pos_x, term.pos_y, term.width, term.height).center())
        for symbol in symbols:
            if (isinstance(symbol, sdlSymbols.State) and [c for c in
                symbol.childSymbols() if isinstance(c, (sdlSymbols.Input,
                    sdlSymbols.Connect, sdlSymbols.ContinuousSignal))]):
                term_branch, term_inators = copy_branch(symbol)
                branch.extend(term_branch)
                res_terminators.extend(term_inators)
    return branch, res_terminators


def paste(parent, scene):
    '''
        Paste previously copied symbols at selection point
    '''
    CLIPBOARD.clear()
    if not parent:
        new_symbols = paste_floating_objects(scene)
    else:
        new_symbols = paste_below_item(parent, scene)
    return new_symbols


def paste_floating_objects(scene):
    ''' Paste items with no parents (states, text areas) '''
    symbols = []
    LOG.debug('PASTING FLOATING OBJECTS')

    for item_list, terminators in COPY_PASTE:
        # states is a list passed as parameter - not a generator:
        start = [i for i in item_list if isinstance(i, ogAST.Start)]
        states = [i for i in item_list if isinstance(i, ogAST.State)]
        text_areas = (i for i in item_list if isinstance(i, ogAST.TextArea))
        labels = (i for i in item_list if isinstance(i, ogAST.Floating_label))
        procedures = (i for i in item_list if isinstance(i, ogAST.Procedure))
        processes = (i for i in item_list if isinstance(i, ogAST.Process))
        for state in states:
            # First check if state has already been pasted
            try:
                new_item = Renderer.render(state, scene=CLIPBOARD,
                           terminators=terminators, states=states)
            except TypeError as err:
                LOG.debug('No paste "' + state.inputString + '" -' + str(err))
                # Discard terminators (explanation given in Renderer._state)
                pass
            else:
                LOG.debug('PASTE STATE "' + state.inputString + '"')
                symbols.append(new_item)
                # Insert the new state at click coordinates
                Renderer.add_to_scene(new_item, scene)
        for each in chain(text_areas, labels):
            LOG.debug('PASTE Text Area/Label')
            new_item = Renderer.render(each, scene, states=states)
            symbols.append(new_item)
        for each in chain(procedures, processes):
            LOG.debug('PASTE Process/Procedure')
            new_item = Renderer.render(each, scene, states=states)
            symbols.append(new_item)
            new_item.nested_scene = scene.create_subscene(
                                               type(new_item).__name__.lower())
            # Render recursively, creating any required scene
            try:
                new_item.nested_scene.render_everything(each.content)
            except TypeError as err:
                LOG.debug(str(err))

        if start:
            start, = start
            LOG.debug('PASTE START')
            for item in scene.visible_symb:
                if isinstance(item, sdlSymbols.Start):
                    raise TypeError('Only one START symbol is possible')
            new_item = Renderer.render(start, scene, states=states)
            symbols.append(new_item)
    return symbols


def paste_below_item(parent, scene):
    ''' Paste items under a selected symbol '''
    LOG.debug('Pasting below item ' + repr(parent)[slice(0, 20)])
    symbols = []
    for item_list, _ in COPY_PASTE:
        states = [i for i in item_list if isinstance(i, ogAST.State)]
        for i in [c for c in item_list if not isinstance
                (c, (ogAST.State, ogAST.TextArea, ogAST.Start))]:
            LOG.debug('PASTE ' + str(i))
            # Create the new item from the AST description
            new_item = Renderer.render(i, scene=CLIPBOARD,
                                       parent=None, states=states)
            # Check that item is compatible with parent
            if (type(new_item).__name__ in parent.allowed_followers):
                # Move the item from the clipboard to the scene
                Renderer.add_to_scene(new_item, scene)
                new_item.pos_x = new_item.pos_y = 0.0
                symbols.append(new_item)
            else:
                raise TypeError('Cannot paste here ({t1} cannot follow {t2}'
                                .format(t1=type(new_item), t2=type(parent)))
    return symbols
