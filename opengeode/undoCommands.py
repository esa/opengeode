#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    OpenGEODE - A tiny SDL Editor for TASTE - Support for Undo/Redo

    Undo/Redo commands for generic symbols when used in a diagram editor.

    Note when creating a new command:
        the redo() function is *called* when the command is created.
        No need to perform the action before.

    Copyright (c) 2012-2015 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from PySide.QtGui import QUndoCommand
from PySide.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation

LOG = logging.getLogger(__name__)


class UndoMacro(object):
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
        super(ReplaceText, self).__init__()
        self.setText('Replace text')
        self.text = text_id
        self.old_text = old_text
        self.new_text = new_text

    def undo(self):
        self.text.setPlainText(self.old_text)

    def redo(self):
        self.text.setPlainText(self.new_text)


class ResizeSymbol(QUndoCommand):
    ''' Undo/Redo command for resizing a symbol '''
    def __init__(self, symbol_id, old_rect, new_rect):
        super(ResizeSymbol, self).__init__()
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
        super(InsertSymbol, self).__init__()
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
            self.scene.refresh()
        except AttributeError:
            pass


class DeleteSymbol(QUndoCommand):
    ''' Undo/Redo command for a symbol deletion '''
    def __init__(self, item):
        super(DeleteSymbol, self).__init__()
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
        super(MoveSymbol, self).__init__()
        self.setText('Move symbol')
        self.symbol = symbol_id
        self.old_pos = old_pos
        self.new_pos = new_pos
        if animate:
            self.animation = QPropertyAnimation(self.symbol, "position")
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
