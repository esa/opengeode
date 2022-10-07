#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module contains the definition of the SDL symbols,
    including geometry and specific symbol behaviour when needed.

    All symbols inherit the generic Vertical- and Horizontal-
    Symbol classes defined in the "genericSymbols.py" module.

    Copyright (c) 2012-2021 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
           'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol',
           'Procedure', 'ProcedureStart', 'ProcedureStop', 'ProcessType',
           'StateStart', 'Process', 'ContinuousSignal']

import traceback
import logging
from itertools import chain

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .genericSymbols import HorizontalSymbol, VerticalSymbol, Comment
from .Connectors import Connection, JoinConnection, Signalroute

from . import ogParser, ogAST


LOG = logging.getLogger('sdlSymbols')

AST = ogAST.AST()
CONTEXT = ogAST.Process()

# SDL-specific: reserved keywords, to be highlighted in textboxes
# Two kind of formatting are possible: black bold, and red bold
SDL_BLACKBOLD = ['\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT', 'FPAR', 'TODO', 'FIXME', 'XXX', 'ENDFOR',
                'CHECKME', 'PROCEDURE', 'EXTERNAL', 'IN', 'OUT', 'TIMER',
                'SET_TIMER', 'RESET_TIMER', 'VIA', 'ENTRY', 'EXIT', 'PRIORITY',
                'SYNTYPE', 'ENDSYNTYPE', 'CONSTANTS', 'ENDPROCEDURE', 'FOR',
                'COMMENT', 'SIGNAL', 'SIGNALLIST', 'USE', 'RETURNS', 'ANY',
                'EXPORTED', 'REFERENCED', 'MONITOR', 'RENAMES', "TO",
                'SUCCESSSTATES', 'ERRORSTATES', 'IGNORESTATES',
                'NEWTYPE', 'ENDNEWTYPE', 'ARRAY', 'STRUCT', 'SYNONYM')]

SDL_REDBOLD = ['\\b{word}\\b'.format(word=word) for word in (
              'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE', 'INTEGER',
              'CHARACTER', 'ASN1INT',
              'TASK', 'PROCESS', 'LABEL', 'JOIN', 'CONNECTION', 'CONNECT')]


def variables_autocompletion(symbol, type_filter=None):
    ''' Intelligent autocompletion for variables - including struct fields
        Optional: only variables of a type listed in type_filter are kept
    '''
    res = set()
    if not symbol.text:
        return res
    sep = "!" if "!" in symbol.text.context else "."
    parts = symbol.text.context.split(sep)
    if len(parts) == 0:
        return res
    elif len(parts) == 1:
        try:
            fpar = {fp['name']: (fp['type'], None) for fp in CONTEXT.fpar}
        except AttributeError:
            # not in the context of a procedure
            fpar = {}
        # Return the list of variables, possibly filtered by type
        if not type_filter:
            res = set( list(CONTEXT.variables.keys())
                      + list(CONTEXT.global_variables.keys())
                      + list(AST.asn1_constants.keys())
                      + list(fpar.keys()))
        else:
            constants = {name: (cty.type, None)
                         for name, cty in AST.asn1_constants.items()}
            try:
                type_filter_names = [ogParser.type_name(ty)
                                     for ty in type_filter]
            except AttributeError as err:
                # This would need to be investigated: it can happen when
                # using a parameter in an input just after the parameter was
                # added to the signal in the block view, and before any
                # variable has been declared....
                LOG.debug(str(err))
                return res
            for name, (asn1type, _) in chain(CONTEXT.variables.items(),
                                          CONTEXT.global_variables.items(),
                                          constants.items(),
                                          fpar.items()):
                if ogParser.type_name(asn1type) in type_filter_names:
                    res.add(name)
    else:
        var = parts[0].lower()
        try:
            var_t = ogParser.find_variable_type(var, CONTEXT)
            basic = ogParser.find_basic_type(var_t, AST.dataview)
            res = (field.replace('-', '_') for field in basic.Children.keys())
        except (AttributeError, TypeError):
            res = []
        else:
            for each in parts[1:-1]:
                try:
                    for child, childtype in basic.Children.items():
                        if child.lower() == each.lower().replace('_', '-'):
                            basic = ogParser.find_basic_type(childtype.type,
                                                             AST.dataview)
                            break
                    else:
                        res = ()
                        break
                except (AttributeError, TypeError):
                    res = ()
                    break
            else:
                try:
                    res = (field.replace('-', '_')
                           for field in basic.Children.keys())
                except AttributeError:
                    res = ()
    return res




# pylint: disable=R0904
class Input(HorizontalSymbol):
    ''' SDL INPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                             'Input', 'Label', 'Connect', 'ContinuousSignal']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']

    common_name = 'input_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ''' Create the INPUT symbol '''
        ast = ast or ogAST.Input()
        self.ast = ast
        self.branch_entrypoint = None
        self.width, self.height = 0, 0
        if not ast.pos_y and parent:
            # Make sure the item is placed below its parent
            ast.pos_y = parent.y() + parent.boundingRect().height() + 10
        super().__init__(parent,
                                    text=ast.inputString,
                                    x=ast.pos_x or 0,
                                    y=ast.pos_y or 0,
                                    hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        gradient = QRadialGradient(50, 50, 50, 50, 50)
        gradient.setColorAt(0, QColor(255, 240, 170))
        gradient.setColorAt(1, Qt.white)
        self.setBrush(QBrush(gradient))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def insert_symbol(self, parent, x, y):
        ''' Insert Input symbol - propagate branch Entry point '''
        # Make sure that parent is a state, not a sibling symbol
        item_parent = (parent if not isinstance(parent, (Input,
                                                         ContinuousSignal))
                       else parent.parentItem())
        self.branch_entrypoint = item_parent.branch_entrypoint
        super().insert_symbol(item_parent, x, y)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)


    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.lineTo(width, 0)
            path.lineTo(width - 11, height / 2)
            path.lineTo(width, height)
            path.lineTo(0, height)
            path.lineTo(0, 0)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in str(self):
            # Input parameter: return the list of variables of this type
            input_name = str(self).split('(')[0].strip().lower()
            asn1_filter = [sig.get('type') for sig in CONTEXT.input_signals if
                           sig['name'] == input_name]
            return variables_autocompletion(self, asn1_filter)
        else:
            # Return the list of input signals and timers
            return (set(sig['name'] for sig in CONTEXT.input_signals).union(
                    CONTEXT.global_timers + CONTEXT.timers))


class Connect(Input):
    ''' Connect point below a nested state '''
    common_name = 'connect_part'
    resizeable = False
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            self.setPen(QPen(Qt.blue))
            self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
            path = QPainterPath()
            path.moveTo(width / 2, 0)
            path.lineTo(width / 2, height)
            #path.moveTo(0, height / 2)
            #path.lineTo(width, height / 2)
            self.setPath(path)
            super(Input, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' Symbol cannot be resized '''
        return

    @property
    def completion_list(self):
        ''' Set auto-completion list: list of exit points of nested state '''
        parent_state = str(self.parentItem()).lower()
        for each in CONTEXT.composite_states:
            if each.statename == parent_state:
                return each.state_exitpoints
        else:
            return set()


# pylint: disable=R0904
class Output(VerticalSymbol):
    ''' SDL OUTPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'output'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output()
        self.ast = ast
        self.width, self.height = 0, 0
        super().__init__(parent=parent,
                text=ast.inputString, x=ast.pos_x or 0, y=ast.pos_y or 0,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)

        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.lineTo(width - 11, 0)
            path.lineTo(width, height / 2)
            path.lineTo(width - 11, height)
            path.lineTo(0, height)
            path.lineTo(0, 0)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in str(self):
            # Output parameter: return the list of variables of this type
            output_name = str(self).split('(')[0].strip().lower()
            asn1_filter = [sig['type'] for sig in CONTEXT.output_signals if
                           hasattr(sig, 'type') and sig['name'] == output_name]
            return variables_autocompletion(self, asn1_filter)
        else:
            # Return the list of output signals
            return (set(sig['name'] for sig in CONTEXT.output_signals))


# pylint: disable=R0904
class Decision(VerticalSymbol):
    ''' SDL DECISION Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                             'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'decision'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD + ['\\b{}\\b'.format(word)
                                   for word in ('AND', 'OR')]
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 50)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Decision()
        self.ast = ast
        self.width, self.height = 0, 0
        # Define the point where all branches of the decision can join again
        self.connectionPoint = QPoint(ast.width / 2, ast.height + 30)
        super().__init__(parent, text=ast.inputString,
                x=ast.pos_x or 0, y=ast.pos_y or 0, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QColor(255, 255, 202))
        self.minDistanceToSymbolAbove = 0
        self.parser = ogParser
        self.text_alignment = Qt.AlignHCenter
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    @property
    def terminal_symbol(self):
        '''
            Compute dynamically if the item is terminal by checking
            if all its branches end with a terminator
        '''
        for branch in self.branches():
            if not branch.last_branch_item.terminal_symbol:
                return False
        return True

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        return chain(variables_autocompletion(self), ('length', 'present'))

    def branches(self):
        ''' Return the list of decision answers (as a generator) '''
        return (branch for branch in self.childSymbols()
                if isinstance(branch, DecisionAnswer))

    def set_shape(self, width, height):
        ''' Define polygon points to draw the symbol '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.moveTo(width / 2, 0)
            path.lineTo(width, height / 2)
            path.lineTo(width / 2, height)
            path.lineTo(0, height / 2)
            path.lineTo(width / 2, 0)
            self.setPath(path)
            super().set_shape(width, height)

    def resize_item(self, rect):
        ''' On resize event, make sure connection points are updated '''
        delta_y = self.boundingRect().height() - rect.height()
        super().resize_item(rect)
        self.connectionPoint.setX(self.boundingRect().center().x())
        self.connectionPoint.setY(self.connectionPoint.y() - delta_y)
        self.update_connections()

    def update_connections(self):
        ''' Redefined - update arrows shape below connection point '''
        super().update_connections()
        for branch in self.branches():
            for cnx in branch.last_branch_item.connections():
                cnx.reshape()
        self.updateConnectionPointPosition()

    def updateConnectionPointPosition(self):
        ''' Compute the joining point of decision branches '''
        new_y = 0
        new_x = self.boundingRect().width() / 2.0
        answers = False
        for branch in self.branches():
            answers = True
            last_cnx = None
            last = branch.last_branch_item
            try:
                # To compute the branch length, we must keep only the symbols,
                # so we must remove the last connection (if any)
                last_cnx, = (c for c in last.childItems() if
                    isinstance(c, Connection) and not
                    isinstance(c.child, (Comment, HorizontalSymbol)))
                # Don't set parent item to None to avoid Qt segfault
                # The bug with setParentItem is a Qt bug documented here:
                # https://bugreports.qt.io/browse/QTBUG-18616
                # the crash may happen if the scene of the new parent
                # is different from the scene of the object. the doc says
                # it is allowed but an assert in the code makes it crash
                # workaround: first put the item manually in the right scene
                # then call setParentItem
                if self.scene() != last_cnx.scene():
                    self.scene().addItem(last_cnx)
                last_cnx.setParentItem(self)
            except ValueError:
                pass
            branch_len = branch.y() + (
                    branch.boundingRect() |
                    branch.childrenBoundingRect()).height()
            try:
                if last.scene() != last_cnx.scene():
                    last.scene().addItem(last_cnx) # workaround Qt's bug 18616
                last_cnx.setParentItem(last)
            except AttributeError:
                pass
            # If last item was a decision, use its connection point
            # position to get the length of the branch:
            try:
                branch_len = (last.connectionPoint.y() +
                        self.mapFromScene(0, last.scenePos().y()).y())
            except AttributeError:
                pass
            # Rounded with int() -> mandatory when view scale has changed
            new_y = int(max(new_y, branch_len))
        if not answers:
            new_y = int(self.boundingRect().height())
        new_y += 15
        delta = new_y - self.connectionPoint.y()
        self.connectionPoint.setY(new_y)
        self.connectionPoint.setX(new_x)
        if delta != 0:
            child = self.next_aligned_symbol()
            try:
                child.pos_y += delta
            except AttributeError:
                pass
        #self.update_connections()


# pylint: disable=R0904
class DecisionAnswer(HorizontalSymbol):
    ''' If Decision is a "switch", DecisionAnswer is a "case" '''
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                        'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'alternative_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 23)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Answer()
        self.ast = ast
        self.width, self.height = 0, 0 #ast.width, ast.height
        self.terminal_symbol = False
        # last_branch_item is used to compute branch length
        # for the connection point positioning
        self.last_branch_item = self
        super().__init__(parent,
                         text=ast.inputString,
                         x=ast.pos_x or 0,
                         y=ast.pos_y or 0,
                         hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.branch_entrypoint = self
        self.parser = ogParser

    def insert_symbol(self, parent, x, y):
        ''' ANSWER-specific insertion behaviour: link to connection point '''
        if not parent:
            return
        # Make sure that parent is not a sibling answer
        item_parent = (parent if not isinstance(parent, DecisionAnswer)
                       else parent.parentItem())
        super().insert_symbol(item_parent, x, y)
        self.last_branch_item.connectionBelow = \
                JoinConnection(self.last_branch_item, item_parent)
        self.text.try_resize()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def set_shape(self, width, height):
        ''' ANSWER has round, disjoint sides - does not fit in a polygon '''
        if width != self.width or height != self.height:
            point = 20
            path = QPainterPath()
            left = QRect(0, 0, point, height)
            right = QRect(width - point, 0, point, height)
            path.arcMoveTo(left, 125)
            path.arcTo(left, 125, 110)
            path.arcMoveTo(right, -55)
            path.arcTo(right, -55, 110)
            path.moveTo(width, height)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        return ['ELSE']


# pylint: disable=R0904
class Join(VerticalSymbol):
    ''' JOIN symbol (GOTO) '''
    arrow_head = 'simple'
    common_name = 'terminator_statement'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        self.ast = ast
        self.width, self.height = 0, 0
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super().__init__(parent,
                                   text=ast.inputString,
                                   x=ast.pos_x,
                                   y=ast.pos_y,
                                   hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = True
        self.parser = ogParser

    def resize_item(self, rect):
        ''' Redefinition of the resize item (block is a square) '''
        size = min(rect.width(), rect.height())
        rect.setWidth(size)
        rect.setHeight(size)
        super().resize_item(rect)

    def set_shape(self, width, height):
        ''' Define the bounding rectangle of the JOIN symbol '''
        if width != self.width or height != self.height:
            circ = min(width, height)
            path = QPainterPath()
            path.addEllipse(0, 0, circ, circ)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list - list of labels '''
        return (label.inputString for label in CONTEXT.labels)

    def update_completion_list(self, pr_text: str) -> None:
        ''' When text was entered, update list of join terminators '''
        ast, _, _, _, _ = self.parser.parseSingleElement(self.common_name,
                                                         pr_text)
        if not ast:
            # in case of syntax error in the symbol text
            return
        for each in (t for t in CONTEXT.terminators if t.kind == 'join'):
            if each.inputString == str(self):
                # Ignore if already defined
                break
        else:
            CONTEXT.terminators.append(ast)


class ProcedureStop(Join):
    ''' Procedure STOP symbol - very similar to JOIN '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        self.ast = ast
        self.width, self.height = 0, 0
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super().__init__(parent, ast)

    def set_shape(self, width, height):
        ''' Define the symbol shape '''
        if width != self.width or height != self.height:
            circ = min(width, height)
            path = QPainterPath()
            path.addEllipse(0, 0, circ, circ)
            point1 = path.pointAtPercent(0.625)
            point2 = path.pointAtPercent(0.125)
            point3 = path.pointAtPercent(0.875)
            point4 = path.pointAtPercent(0.375)
            path.moveTo(point1)
            path.lineTo(point2)
            path.moveTo(point3)
            path.lineTo(point4)
            self.setPath(path)
            # call Join superclass, otherwise symbol will take Join shape
            super(Join, self).set_shape(circ, circ)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        try:
            return CONTEXT.state_exitpoints
        except AttributeError:
            # Not in a state but in a procedure
            return set()

    def update_completion_list(self, pr_text):
        ''' When text was entered, if in a nested state update exit points '''
        ast, _, _, _, _ = self.parser.parseSingleElement(self.common_name,
                                                         pr_text)
        if not ast:
            # in case of syntax error in the symbol text
            return
        try:
            CONTEXT.state_exitpoints.add(str(self))
        except AttributeError:
            # No state exit points in a procedure
            pass


# pylint: disable=R0904
class Label(VerticalSymbol):
    ''' LABEL symbol '''
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Label()
        self.ast = ast
        self.width, self.height = 0, 0
        super().__init__(parent,
                                    text=ast.inputString,
                                    x=ast.pos_x or 0,
                                    y=ast.pos_y or 0,
                                    hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = False
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    @property
    def common_name(self):
        return 'label' if self.hasParent else 'floating_label'

    def set_shape(self, width, height):
        ''' Define the shape of the LABEL symbol '''
        if width != self.width or height != self.height:
            circ = 35 / 2
            path = QPainterPath()
            path.addEllipse(width / 2 - 35, circ, circ, circ)
            path.moveTo(width / 2 - circ, 35 * 3 / 4)
            path.lineTo(width / 2, 35 * 3 / 4)
            # Add arrow head
            path.moveTo(width / 2 - 5, 35 * 3 / 4 - 5)
            path.lineTo(width / 2, 35 * 3 / 4)
            path.lineTo(width / 2 - 5, 35 * 3 / 4 + 5)
            # Add vertical line in the middle of the symbol
            path.moveTo(width / 2, 0)
            path.lineTo(width / 2, height)
            # Make sure the bounding rect is withing specifications
            path.moveTo(width, height)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list - list of JOIN '''
        return (term.inputString
                for term in CONTEXT.terminators if term.kind == 'join')

    def update_completion_list(self, pr_text):
        ''' When text was entered, update list of labels in current context '''
        ast, _, _, _, _ = self.parser.parseSingleElement(self.common_name,
                                                         pr_text)
        if not ast:
            # in case of syntax error in the symbol text
            return
        for each in CONTEXT.labels:
            if each.inputString == str(self):
                # Ignore if already defined
                break
        else:
            CONTEXT.labels.append(ast)


# pylint: disable=R0904
class Task(VerticalSymbol):
    ''' TASK symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'task'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ''' Initializes the TASK symbol '''
        ast = ast or ogAST.Task()
        self.ast = ast
        self.width, self.height = 0, 0
        super().__init__(parent,
                                   text=ast.inputString,
                                   x=ast.pos_x or 0,
                                   y=ast.pos_y or 0,
                                   hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.lineTo(width, 0)
            path.lineTo(width, height)
            path.lineTo(0, height)
            path.lineTo(0, 0)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        elems = str(self).lower().strip().split()
        asn1_filter = []
        if len(elems) == 2 and elems[1] == ':=':
            # Find type of variable on the left and filter accordingly
            varname = elems[0]
            try:
                fpar = {fp['name']: (fp['type'], None) for fp in CONTEXT.fpar}
            except AttributeError:
                # not in the context of a procedure
                fpar = {}
            constants = {name: (cty.type, None)
                         for name, cty in AST.asn1_constants.items()}
            for name, (asn1ty, _) in chain (CONTEXT.variables.items(),
                                          CONTEXT.global_variables.items(),
                                          constants.items(),
                                          fpar.items()):
                if name == varname:
                    asn1_filter = [asn1ty]
                    break
        return chain(variables_autocompletion(self, asn1_filter),
                     ogParser.SPECIAL_OPERATORS.keys())

# pylint: disable=R0904
class ProcedureCall(VerticalSymbol):
    ''' PROCEDURE CALL symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'procedure_call'
    # Define reserved keywords for the syntax highlighter
    blackbold = ['\\bWRITELN\\b', '\\bWRITE\\b', '\\bTO\\b',
                 '\\bSET_TIMER\\b', '\\bRESET_TIMER\\b']
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output(defName='')
        self.ast = ast
        self.width, self.height = 0, 0
        super().__init__(parent,
                                            text=ast.inputString,
                                            x=ast.pos_x or 0,
                                            y=ast.pos_y or 0,
                                            hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.addRect(0, 0, width, height)
            path.moveTo(7, 0)
            path.lineTo(7, height)
            path.moveTo(width - 7, 0)
            path.lineTo(width - 7, height)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in str(self):
            # Get the variables of the type of the current parameter
            count = str(self).count(',')
            procname = str(self).split('(')[0].strip().lower()
            for each in (proc for proc in CONTEXT.procedures
                         if proc.inputString.lower() == procname):
                param_types = [p['type'] for p in each.fpar]
                break
            else:
                # Procedure not defined, check special operators
                if (procname == 'set_timer' and count == 1) or (
                        procname == 'reset_timer' and count == 0):
                    return chain(CONTEXT.timers, CONTEXT.global_timers)
                elif procname in ('write', 'writeln'):
                    # Could filter for OCTET STRINGS/Strings/Integer/Booleans
                    return variables_autocompletion(self)
                else:
                    return ()
            if count + 1 > len(param_types):
                # User tries to set more parameters than defined
                return ()
            else:
                # Return variables of the type of the parameter
                asn1_filter = param_types[slice(count, count + 1)]
                return variables_autocompletion(self, asn1_filter)
        else:
            return chain((proc.inputString for proc in CONTEXT.procedures),
                         ('set_timer', 'reset_timer', 'write', 'writeln'))


# pylint: disable=R0904
class TextSymbol(HorizontalSymbol):
    ''' Text symbol - used to declare variables, etc. '''
    common_name = 'text_area'
    default_size = 'any'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    # Minimum size for symbol
    min_size = (170, 140)

    def __init__(self, ast=None):
        ''' Create a Text Symbol '''
        ast = ast or ogAST.TextArea()
        self.ast = ast
        self.width, self.height = 0, 0
        super().__init__(parent=None,
                                         text=ast.inputString,
                                         x=ast.pos_x or 0,
                                         y=ast.pos_y or 0,
                                         hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(249, 249, 249)))
        self.terminal_symbol = False
        self.position = QPointF(ast.pos_x or 0, ast.pos_y or 0)
        # Disable hyperlinks for Text symbols
        self._no_hyperlink = True
        # Text is not centered in the box - change default alignment:
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    def check_syntax(self, pr_text):
        ''' Redefinition of the check syntax function for the text symbol '''
        # Standard behaviour except that we permit the last character to be
        # a semi-colon, since that is always the case with declarations
        # and the text box cannot be followed by a COMMENT symbol
        return super().check_syntax(pr_text, check_last_semi=False);


    def update_completion_list(self, pr_text):
        ''' When text was entered, update list of variables/FPAR/Timers '''
        # note, on standalone systems, if the textbox contains a
        # USE Dataview comment 'file.asn'. this file is parsed when leaving
        # the textbox. This gives the impression that this function is slow,
        # it it is not! - no need to investigate performance issues here
        # Get AST for the symbol
        ast, _, _, _, _ = self.parser.parseSingleElement('text_area', pr_text)
        if not ast:
            # in case of syntax error in the symbol text
            return
        try:
            CONTEXT.variables.update(ast.variables)
            CONTEXT.timers = list(set(CONTEXT.timers + ast.timers))
        except AttributeError:
            # context may not have variables/timers (eg if context = block)
            pass
        try:
            existing = {proc.inputString.lower()
                       for proc in CONTEXT.procedures}
            CONTEXT.procedures += [proc for proc in ast.procedures
                                   if proc.inputString.lower() not in existing]
            CONTEXT.fpar.extend(ast.fpar)
        except AttributeError:
            pass
        # Update completion list of Signalroutes
        try:
            Signalroute.completion_list |= set(sig['name']
                                               for sig in ast.signals)
            # Here: update input signals of the process AST since the
            # signature of the signals may have changed...TODO
            CONTEXT.signals += ast.signals
        except AttributeError:
            # no AST, e.g. in case of syntax errors in the text area
            pass

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        try:
            return set(AST.dataview.keys())
        except AttributeError:
            return [] # No Dataview

    def set_shape(self, width, height):
        ''' Define the polygon of the text symbol '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.moveTo(width - 10, 0)
            path.lineTo(0, 0)
            path.lineTo(0, height)
            path.lineTo(width, height)
            path.lineTo(width, 10)
            path.lineTo(width - 10, 10)
            path.lineTo(width - 10, 0)
            path.lineTo(width, 10)
            self.setPath(path)
            super().set_shape(width, height)

    def resize_item(self, rect):
        ''' Text Symbol only resizes down or right '''
        if self.grabber.resize_mode.endswith('left'):
            return
        self.prepareGeometryChange()
        self.set_shape(rect.width(), rect.height())


# pylint: disable=R0904
class State(VerticalSymbol):
    ''' SDL STATE Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Input', 'Connect', 'ContinuousSignal']
    arrow_head = 'simple'
    common_name = 'terminator_statement'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    context_name = "state"

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.State()
        self.ast = ast
        self.width, self.height = 0, 0
        ast.inputString = getattr(ast, 'via', None) or ast.inputString
        super().__init__(parent=parent,
                                    text=ast.inputString,
                                    x=ast.pos_x or 0,
                                    y=ast.pos_y or 0,
                                    hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        self.terminal_symbol = True
        if parent:
            try:
                # Map AST scene coordinates to get actual position
                self.position += self.mapFromScene(ast.pos_x or 0,
                                                   ast.pos_y or 0)
            except TypeError:
                self.update_position()
        else:
            # Use scene coordinates to position
            self.position = QPointF(ast.pos_x or 0, ast.pos_y or 0)
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    @property
    def allow_nesting(self):
        ''' Redefinition - must be checked according to context '''
        # nesting permitted only if single plain state
        result = not any(elem in str(self).lower().strip()
                for elem in ('-', ',', '*', ':', 'via'))
        return result

    @property
    def nested_scene(self):
        ''' Redefined - nested scene per state must be unique '''
        return self._nested_scene

    def double_click(self):
        ''' Catch a double click - Set nested scene '''
        for each, value in self.scene().composite_states.items():
            if str(self).split()[0].lower() == str(each):
                self.nested_scene = value
                break
        else:
            self.nested_scene = None

    @nested_scene.setter
    def nested_scene(self, value):
        ''' Set the value of the nested scene '''
        self._nested_scene = value

    def update_completion_list(self, pr_text):
        ''' When text was entered, update state completion list '''
        # Get AST for the symbol and update the context dictionary
        ast, _, _, _, _ = self.parser.parseSingleElement('state', pr_text)
        if ast:
            # None if there were syntax errors in the symbol
            for each in ast.statelist:
                CONTEXT.mapping[each.lower()] = None

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        elems = str(self).lower().strip().split()
        if len(elems) == 2 and elems[1] == 'via':
            # Get list of entry point of the nested state
            # check if it is an instance
            name = elems[0].split(':')
            if len(name) == 2:
                statename = name[1]
            else:
                statename = name[0]
            for each in CONTEXT.composite_states:
                if each.statename == statename:
                    return each.state_entrypoints
            # the entry points may not be defined yet
            return set()
        else:
            return set(state for state in CONTEXT.mapping if state != 'START')

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if self.nested_scene and self.is_composite():
            # Distinguish composite states with dash line
            self.setPen(QPen(Qt.DashLine))
        else:
            self.setPen(QPen(Qt.SolidLine))

        if width != self.width or height != self.height:
            path = QPainterPath()
            path.addRoundedRect(0, 0, width, height, height / 4, height)
            self.setPath(path)
            super().set_shape(width, height)

    def get_ast(self, pr_text):
        ''' Redefinition of the get_ast function for the state '''
        ast, _, _, _, terminators = self.parser.parseSingleElement('state',
                                                                   pr_text)
        return ast, terminators

    def check_syntax(self, pr_text):
        ''' Redefinition of the check syntax function for the state '''
        name = self.common_name if self.hasParent else 'state'
        _, err, _, _, _ = \
                self.parser.parseSingleElement(name, pr_text)
        return err


class Process(HorizontalSymbol):
    ''' Process symbol '''
    _unique_followers = ['Comment']
    _allow_nesting = True
    default_size = 'any'
    common_name = 'process_definition'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = True #(False to allow multiple processes)
    arrow_head = 'angle'
    arrow_tail = 'angle'
    # Process can be connected to other processes by the user
    user_can_connect = True
    _conn_sources = ['Process']
    _conn_targets = ['Process']
    context_name = "process"

    # Minimum size for symbol
    min_size = (150, 75)

    def __init__(self,
                 ast=None,
                 subscene=None):
        ast = ast or ogAST.Process()
        self.ast = ast
        self.width, self.height = 0, 0
        label = (ast.processName or "") + (': {}'
                                            .format(ast.instance_of_name)
                                            if ast.instance_of_name else '')
        # At creation, call the init of Horizontal symbol, which creates
        # the TextInteraction instance, which calls try_resize, which
        # makes a call to resize_item, which calls set_shape using a size
        # defined by the label. set shape will then be called again using
        # the ast-defined size.
        super().__init__(parent=None,
                         text=label,
                         x=ast.pos_x,
                         y=ast.pos_y,
                         hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene
        self.input_signals = ast.input_signals
        self.output_signals = ast.output_signals
        self.insert_symbol(None, self.x(), self.y())

    @property
    def conn_start_zones(self):
        ''' Redefined - define the zones in the symbol from which user can
        start a connection with another symbol '''
        rect = self.boundingRect()
        yield QRect(15, 5, rect.width() - 30, 10)
        yield QRect(5, 5, 10, rect.height() - 10)
        yield QRect(rect.width() - 15, 5, 10, rect.height() - 10)
        yield QRect(15, rect.height() - 15, rect.width() - 30, 10)

    @property
    def conn_end_zones(self):
        ''' Redefined - define the zones that can receive a connection '''
        rect = self.boundingRect()
        yield QRect(15, 5, rect.width() - 30, 10)
        yield QRect(5, 5, 10, rect.height() - 10)
        yield QRect(rect.width() - 15, 5, 10, rect.height() - 10)
        yield QRect(15, rect.height() - 15, rect.width() - 30, 10)

    def insert_symbol(self, parent, x, y):
        ''' Redefinition - adds connection line to env '''
        super().insert_symbol(parent, x, y)
        if not self.connection:
            self.connection = self.connect_to_parent()

    def connect_to_parent(self):
        ''' Redefinition: creates connection to env with a signalroute '''
        return Signalroute(self)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        #LOG.debug(traceback.print_stack())
        if width != self.width or height != self.height:
            # Don't compute a new path if size has not changed
            path = QPainterPath()
            path.moveTo(7, 0)
            path.lineTo(0, 7)
            path.lineTo(0, height - 7)
            path.lineTo(7, height)
            path.lineTo(width - 7, height)
            path.lineTo(width, height - 7)
            path.lineTo(width, 7)
            path.lineTo(width - 7, 0)
            path.lineTo(7, 0)
            self.setPath(path)
            super().set_shape(width, height)

    def cam_group(self):
        ''' Redefine the graphical boundaries of the item to apply the CAM
            If process has child connections (connections to other processes)
            the CAM group should only include the process block itself,
            not all the lines around it '''
        return self.sceneBoundingRect()

    def mouse_move(self, event):
        ''' In addition to default behaviour: update channel connections '''
        #super().mouse_move(event)
        if self.mode == 'Move':
            event_pos = event.pos()
            new_y = self.pos_y + (event_pos.y() - event.lastPos().y())
            new_x = self.pos_x + (event_pos.x() - event.lastPos().x())
            self.position = QPointF(new_x, new_y)
            # Signal the move to the connections
            self.moved.emit(event.lastPos().x() - event.pos().x(),
                            event.lastPos().y() - event.pos().y())


    def update_completion_list(self, pr_text):
        ''' When text was entered, update completion list at block level '''
        for each in CONTEXT.processes:
            if str(self.text).lower() == each.processName:
                break
        else:
            new_proc = ogAST.Process()
            new_proc.processName = str(self.text).lower()
            CONTEXT.processes.append(new_proc)


class Procedure(Process):
    ''' Procedure declaration symbol - Very similar to Process '''
    _unique_followers = ['Comment']
    _allow_nesting = True
    common_name = 'procedure'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = False
    user_can_connect = False
    context_name = "procedure"

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Procedure()
        self.ast = ast
        self.width, self.height = 0, 0
        super(Process, self).__init__(parent=None,
                                      text=ast.inputString,
                                      x=ast.pos_x or 0,
                                      y=ast.pos_y or 0,
                                      hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene

    def insert_symbol(self, parent, x, y):
        ''' Redefinition - no connection line to env '''
        super(Process, self).insert_symbol(parent, x, y)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.addRect(7, 0, width - 14, height)
            path.moveTo(7, 0)
            path.lineTo(0, 7)
            path.lineTo(0, height - 7)
            path.lineTo(7, height)
            path.moveTo(width - 7, 0)
            path.lineTo(width, 7)
            path.lineTo(width, height - 7)
            path.lineTo(width - 7, height)
            self.setPath(path)
            super(Process, self).set_shape(width, height)

    def update_completion_list(self, pr_text):
        ''' When text was entered, update completion list of ProcedureCall '''
        for each in CONTEXT.procedures:
            if str(self.text).lower() == each.inputString:
                break
        else:
            new_proc = ogAST.Procedure()
            new_proc.inputString = str(self.text).lower()
            CONTEXT.procedures.append(new_proc)

class ProcessType(Procedure):
    ''' PROCESS TYPE (floating symbol with no connections '''
    _unique_followers = ['Comment']
    _allow_nesting = True
    common_name = 'process_definition'
    context_name = 'process'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = False
    user_can_connect = False
    
    # Minimum size for symbol
    min_size = (150, 75)

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Process()
        ast.process_type = True
        self.ast = ast
        self.width, self.height = 0, 0
        super(Process, self).__init__(parent=None,
                                      text=ast.processName,
                                      x=ast.pos_x or 0,
                                      y=ast.pos_y or 0,
                                      hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            # Fill rule makes sure the full symbol is colored
            path.setFillRule(Qt.WindingFill)
            path.moveTo(7, 0)
            path.lineTo(0, 7)
            path.lineTo(0, height - 7)
            path.lineTo(7, height)
            path.lineTo(width - 7, height)
            path.lineTo(width, height - 7)
            path.lineTo(width, 7)
            path.lineTo(width - 7, 0)
            path.lineTo(7, 0)
            # inner shape
            path.moveTo(12, 7)
            path.lineTo(7, 12)
            path.lineTo(7, height - 12)
            path.lineTo(12, height - 7)
            path.lineTo(width - 12, height - 7)
            path.lineTo(width - 7, height - 12)
            path.lineTo(width - 7, 12)
            path.lineTo(width - 12, 7)
            path.lineTo(12, 7)
            self.setPath(path)
            super(Process, self).set_shape(width, height)

    def update_completion_list(self, pr_text):
        ''' After text is entered in process type, don't update any context '''
        # Todo perhaps later for autocompletion of process instances
        pass

# pylint: disable=R0904
class Start(HorizontalSymbol):
    ''' SDL START Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    # There cannot be more than one START symbol in a scene
    is_singleton = True
    common_name = 'start'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    has_text_area = False

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, ast=None):
        ''' Create the START symbol '''
        ast = ast or ogAST.Start()
        self.ast = ast
        self.terminal_symbol = False
        self.width, self.height = 0, 0
        super().__init__(parent=None,
                                    text=ast.inputString[slice(0, -6)],
                                    x=ast.pos_x or 0,
                                    y=ast.pos_y or 0,
                                    hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        # No hyperlink for START symbol because it has no text
        self._no_hyperlink = True
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' User cannot enter text in the START symbol - Return dummy text '''
        return u'START'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.addRoundedRect(0, 0, width, height, height / 2, height / 2)
            self.setPath(path)
            super().set_shape(width, height)


class ProcedureStart(Start):
    ''' Start symbol of a procedure - only shape differs from Start '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    common_name = 'proc_start'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.addRoundedRect(0, 0, width, height, height / 2, height / 2)
            path.moveTo(min(width / 2, height / 2), 0)
            path.lineTo(min(width / 2, height / 2), height)
            path.moveTo(max(width / 2, width - height / 2), 0)
            path.lineTo(max(width / 2, width - height / 2), height)
            self.setPath(path)
            super(Start, self).set_shape(width, height)


class StateStart(Start):
    ''' Composite states can have several named START symbols '''
    has_text_area = True
    is_singleton = False
    common_name = 'state_start'

    def __str__(self):
        ''' Return the state entry point '''
        return str(self.text)

    def update_completion_list(self, pr_text):
        ''' Update nested state entry points '''
        CONTEXT.state_entrypoints.add(str(self))


# pylint: disable=R0904
class ContinuousSignal(HorizontalSymbol):
    ''' " Provided" part below a state - not a enabling condition '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                             'Input', 'Label', 'Connect', 'ContinuousSignal']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'continuous_signal'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD.copy()
    redbold = SDL_REDBOLD.copy()
    redbold.remove("\\bINPUT\\b")
    redbold.remove("\\bOUTPUT\\b")
    redbold.remove("\\bSTATE\\b")
    blackbold.append("\\bINPUT\\b")
    blackbold.append("\\bOUTPUT\\b")
    blackbold.append("\\bAND\\b")
    blackbold.append("\\bFROM\\b")
    blackbold.append("\\bTO\\b")

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, parent=None, ast=None):
        ''' Create the Provided symbol - use no background color '''
        ast = ast or ogAST.ContinuousSignal()
        self.ast = ast
        self.branch_entrypoint = None
        self.width, self.height = 0, 0
        if not ast.pos_y and parent:
            # Make sure the item is placed below its parent
            ast.pos_y = parent.y() + parent.boundingRect().height() + 10
        super().__init__(parent, text=ast.inputString,
                x=ast.pos_x or 0, y=ast.pos_y or 0, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def insert_symbol(self, parent, x, y):
        ''' Insert symbol - propagate branch Entry point '''
        # Make sure that parent is a state, not a sibling symbol
        item_parent = (parent if not isinstance(parent, (Input,
                                                         ContinuousSignal))
                       else parent.parentItem())
        self.branch_entrypoint = item_parent.branch_entrypoint
        super().insert_symbol(item_parent, x, y)

    def set_shape(self, width, height):
        ''' Define the shape '''
        if width != self.width or height != self.height:
            path = QPainterPath()
            path.moveTo(15, 0)
            path.lineTo(0, height / 2.0)
            path.lineTo(15, height)
            is_observer = self.ast.observer
            if isinstance(CONTEXT, ogAST.Process) and CONTEXT.monitors:
                is_observer = True
            if is_observer:
                self.setBrush(QBrush(QColor(255, 248, 221)))
                # If there are monitors, it is an observer
                # -> change slightly the symbol shape
                path.lineTo(width - 15, height)
            else:
                path.moveTo(width - 15, height)
            path.lineTo(width, height / 2.0)
            path.lineTo(width - 15, 0)
            if is_observer:
                path.lineTo(15, 0)
            self.setPath(path)
            super().set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        return variables_autocompletion(self, None)
