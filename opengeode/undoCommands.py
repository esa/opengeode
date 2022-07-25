#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    OpenGEODE - A tiny SDL Editor for TASTE - Support for Undo/Redo

    Undo/Redo commands for generic symbols when used in a diagram editor.

    Note when creating a new command:
        the redo() function is *called* when the command is created.
        No need to perform the action before.

    Copyright (c) 2012-2020 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import Pr
from . import ogParser

LOG = logging.getLogger(__name__)


class UndoMacro:
    ''' Context manager for Undo macros '''

    def __init__(self, stack, text):
        ''' Create context manager '''
        self.stack = stack
        self.text = text

    def __enter__(self):
        ''' Create macro for a set of undo commands '''
        self.stack.beginMacro(self.text)

    def __exit__(self, atype, value, traceback):
        ''' Stop the recording of undo commands '''
        self.stack.endMacro()


class ReplaceText(QUndoCommand):
    ''' Undo/Redo command for updating the text in a symbol '''
    def __init__(self, text_id, old_text, new_text):
        super().__init__()
        self.setText('Replace text')
        self.text = text_id
        self.old_text = old_text
        self.new_text = new_text
        self.scene = self.text.parent.scene()
        self.count_instances_old, self.count_instances_new = 1, -1
        for each in self.scene.states:
            # count the number of instances of the states in the scene
            # the text is already renamed, values are initialized to -1 and 1
            state_name = str(each).lower()
            if self.old_text.lower() == state_name:
                self.count_instances_old += 1
            if self.new_text.lower() == state_name:
                self.count_instances_new += 1

    def undo(self):
        self.text.setPlainText(self.old_text)
        if self.text.parent in self.scene.states:
            # see explanations in the redo() function below
            if self.count_instances_new != 0:
                pass
            else:
                if self.count_instances_old == 1:
                    try:
                        self.scene.composite_states[self.old_text.lower()] = \
                         self.scene.composite_states.pop(self.new_text.lower())
                    except KeyError:
                        pass
                else:
                    # scene was created with redo, delete reference
                    try:
                        self.scene.composite_states.pop(self.new_text.lower())
                    except KeyError:
                        pass

    def redo(self):
        self.text.setPlainText(self.new_text)

        if self.text.parent in self.scene.states:
            # renaming a state in case of a nested state:
            # 1) if renamed state already exists, do nothing special
            # 2) if renamed state is a new state:
            #    a. if this was the only instance of the state, just rename
            #       the list of composite state to reflect the new state name
            #    b. otherwise, parse the composite state, create a new scene
            #       and render the same content in the new scene, then
            #       update the list of composite states with the new copy
            if self.count_instances_new != 0:
                # case 1: do nothing, state is already initialized
                pass
            else:
                if self.count_instances_old == 1:
                    # case 2a. rename the list of composite states
                    try:
                        self.scene.composite_states[self.new_text.lower()] = \
                         self.scene.composite_states.pop(self.old_text.lower())
                    except KeyError:
                        pass
                else:
                    # case 2b: create a new scene and really copy the state
                    state = self.text.parent
                    if state.is_composite():
                        # Parse the scene of the nested state:
                        sub_state = u'\n'.join(Pr.generate(state,
                                                           composite=True,
                                                           nextstate=False))
                        if sub_state:
                            new_scene = self.scene.create_subscene(
                                    context=state.context_name,
                                    parent=self.scene)
                            # get the AST of type ogAST.CompositeState
                            ast, _, _, _, _ = ogParser.parseSingleElement(
                                    elem='composite_state',
                                    string=sub_state)
                            # render the composite state content
                            new_scene.render_everything(ast.content)
                            self.scene.composite_states[
                                    self.new_text.lower()] = new_scene


class ResizeSymbol(QUndoCommand):
    ''' Undo/Redo command for resizing a symbol '''
    def __init__(self, symbol_id, old_rect, new_rect):
        super().__init__()
        self.setText('Resize symbol')
        self.symbol = symbol_id
        self.old_rect = old_rect
        self.new_rect = new_rect

    def undo(self):
        try:
            self.symbol.resize_item(self.old_rect)
            # Update grabber size
            self.symbol.grabber.display()
        except AttributeError:
            # Not all symbols can be resized
            pass

    def redo(self):
        try:
            self.symbol.resize_item(self.new_rect)
            # Update grabber size
            self.symbol.grabber.display()
        except AttributeError:
            # Not all symbols can be resized
            pass


class InsertSymbol(QUndoCommand):
    ''' Undo/Redo command for inserting a new item '''
    def __init__(self, item, parent, pos):
        super().__init__()
        self.item = item
        self.parent = parent
        self.pos_x = pos.x() if pos else None
        self.pos_y = pos.y() if pos else None
        try:
            self.scene = item.scene() or parent.scene()
        except AttributeError:
            LOG.debug('NO SCENE TO INSERT "' + str(item) + '"')

    def undo(self):
        self.pos_x = self.item.x()
        self.pos_y = self.item.y()
        self.item.delete_symbol()
        # Replaced removeItem with hide/show to avoid exit crash
        self.item.hide()

    def redo(self):
        try:
            if self.item not in self.scene.items():
                self.scene.addItem(self.item)
        except AttributeError:
            pass
        self.item.insert_symbol(self.parent, self.pos_x, self.pos_y)
        # Replaced removeItem with hide/show to avoid exit crash
        self.item.show()
        self.item.grabber.display()
        try:
            # Immediate refresh for a better rendering, however slows down
            # performance when inserting decisions in a complex model
            #self.scene.refresh()
            # Update only the connections - this is much faster
            self.item.update_connections()
        except AttributeError:
            pass


class DeleteSymbol(QUndoCommand):
    ''' Undo/Redo command for a symbol deletion '''
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.scene = item.scene()
        self.parent = item.parentItem() if item.hasParent else None
        self.pos_x = 0
        self.pos_y = 0

    def undo(self):
        self.item.insert_symbol(self.parent, self.pos_x, self.pos_y)
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        # Replaced removeItem with hide/show to avoid exit crash
        self.item.show()
        self.scene.refresh()

    def redo(self):
        self.pos_x = self.item.x()
        self.pos_y = self.item.y()
        self.item.delete_symbol()
        # Replaced removeItem with hide/show to avoid exit crash
        self.item.hide()
        self.scene.refresh()


class MoveSymbol(QUndoCommand):
    ''' Undo/Redo command for moving symbols '''
    def __init__(self, symbol_id, old_pos, new_pos, animate=False):
        super().__init__()
        self.setText('Move symbol')
        self.symbol = symbol_id
        self.old_pos = old_pos
        self.new_pos = new_pos
        if animate:
            self.animation = QPropertyAnimation(self.symbol, b"position")
            self.animation.setDuration(500)
            self.animation.setStartValue(self.old_pos)
            self.animation.setEndValue(self.new_pos)
            self.animation.setEasingCurve(QEasingCurve.OutCirc)

    def undo(self):
        ''' Undo a symbol move '''
        self.symbol.position = self.old_pos
        try:
            self.symbol.decisionParent.updateConnectionPointPosition()
        except AttributeError:
            pass

    def redo(self):
        ''' Apply a symbol move '''
        try:
            self.animation.start()
        except AttributeError:
            self.symbol.position = self.new_pos
        try:
            self.symbol.decisionParent.updateConnectionPointPosition()
        except AttributeError:
            pass
