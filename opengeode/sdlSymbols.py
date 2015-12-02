#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module contains the definition of the SDL symbols,
    including geometry and specific symbol behaviour when needed.

    All symbols inherit the generic Vertical- and Horizontal-
    Symbol classes defined in the "genericSymbols.py" module.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
           'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol',
           'Procedure', 'ProcedureStart', 'ProcedureStop', 'ASN1Viewer',
           'StateStart', 'Process', 'ContinuousSignal']

#import traceback
import logging
from itertools import chain

from PySide.QtCore import Qt, QPoint, QRect, QRectF, QPointF
from PySide.QtGui import(QPainterPath, QBrush, QColor, QRadialGradient, QPen)

from genericSymbols import HorizontalSymbol, VerticalSymbol, Comment
from Connectors import Connection, JoinConnection, Signalroute

import ogParser
import ogAST


LOG = logging.getLogger('sdlSymbols')

AST = ogAST.AST()
CONTEXT = ogAST.Process()

# SDL-specific: reserved keywords, to be highlighted in textboxes
# Two kind of formatting are possible: black bold, and red bold
SDL_BLACKBOLD = ['\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT', 'FPAR', 'TODO', 'FIXME', 'XXX',
                'CHECKME', 'PROCEDURE', 'EXTERNAL', 'IN', 'OUT', 'TIMER',
                'SET_TIMER', 'RESET_TIMER', 'VIA', 'ENTRY', 'EXIT', 'ANY',
                'SYNTYPE', 'ENDSYNTYPE', 'CONSTANTS', 'ENDPROCEDURE',
                'COMMENT', 'SIGNAL', 'SIGNALLIST', 'USE', 'RETURNS'
                'NEWTYPE', 'ENDNEWTYPE', 'ARRAY', 'STRUCT', 'SYNONYM')]

SDL_REDBOLD = ['\\b{word}\\b'.format(word=word) for word in (
              'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE',
              'TASK', 'PROCESS', 'LABEL', 'JOIN', 'CONNECTION', 'CONNECT')]


def variables_autocompletion(symbol, type_filter=None):
    ''' Intelligent autocompletion for variables - including struct fields
        Optional: only variables of a type listed in type_filter are kept
    '''
    res = set()
    if not symbol.text:
        return res
    parts = symbol.text.context.split('!')
    if len(parts) == 0:
        return res
    elif len(parts) == 1:
        try:
            fpar = {fp['name']: (fp['type'], None) for fp in CONTEXT.fpar}
        except AttributeError:
            # not in the context of a procedure
            fpar = {}
        # Return the list of variables, possibly filterd by type
        if not type_filter:
            res = set(CONTEXT.variables.keys()
                      + CONTEXT.global_variables.keys()
                      + AST.asn1_constants.keys()
                      + fpar.keys())
        else:
            constants = {name: (cty.type, None)
                         for name, cty in AST.asn1_constants.viewitems()}
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
            for name, (asn1type, _) in chain(CONTEXT.variables.viewitems(),
                                          CONTEXT.global_variables.viewitems(),
                                          constants.viewitems(),
                                          fpar.viewitems()):
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
                    for child, childtype in basic.Children.viewitems():
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

    def __init__(self, parent=None, ast=None):
        ''' Create the INPUT symbol '''
        ast = ast or ogAST.Input()
        self.ast = ast
        self.branch_entrypoint = None
        if not ast.pos_y and parent:
            # Make sure the item is placed below its parent
            ast.pos_y = parent.y() + parent.boundingRect().height() + 10
        super(Input, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x or 0, y=ast.pos_y or 0, hyperlink=ast.hyperlink)
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
        super(Input, self).insert_symbol(item_parent, x, y)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width - 11, height / 2)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Input, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in unicode(self):
            # Input parameter: return the list of variables of this type
            input_name = unicode(self).split('(')[0].strip().lower()
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
    auto_expand = True
    resizeable = False
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        self.setPen(QPen(Qt.blue))
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0, height)
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
        parent_state = unicode(self.parentItem()).lower()
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

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output()
        self.ast = ast
        super(Output, self).__init__(parent=parent,
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
        path = QPainterPath()
        path.lineTo(width - 11, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width - 11, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Output, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in unicode(self):
            # Output parameter: return the list of variables of this type
            output_name = unicode(self).split('(')[0].strip().lower()
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

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Decision()
        self.ast = ast
        # Define the point where all branches of the decision can join again
        self.connectionPoint = QPoint(ast.width / 2, ast.height + 30)
        super(Decision, self).__init__(parent, text=ast.inputString,
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
        path = QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super(Decision, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' On resize event, make sure connection points are updated '''
        delta_y = self.boundingRect().height() - rect.height()
        super(Decision, self).resize_item(rect)
        self.connectionPoint.setX(self.boundingRect().center().x())
        self.connectionPoint.setY(self.connectionPoint.y() - delta_y)
        self.update_connections()

    def update_connections(self):
        ''' Redefined - update arrows shape below connection point '''
        super(Decision, self).update_connections()
        for branch in self.branches():
            for cnx in branch.last_branch_item.connections():
                cnx.reshape()

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
                last_cnx.setParentItem(self)
            except ValueError:
                pass
            branch_len = branch.y() + (
                    branch.boundingRect() |
                    branch.childrenBoundingRect()).height()
            try:
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
        self.update_connections()


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

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Answer()
        self.ast = ast
        self.width, self.height = ast.width, ast.height
        self.terminal_symbol = False
        # last_branch_item is used to compute branch length
        # for the connection point positionning
        self.last_branch_item = self
        super(DecisionAnswer, self).__init__(parent,
                                             text=ast.inputString,
                                             x=ast.pos_x or 0,
                                             y=ast.pos_y or 0,
                                             hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.branch_entrypoint = self
        self.parser = ogParser

    def insert_symbol(self, parent, x, y):
        ''' ANSWER-specific insersion behaviour: link to connection point '''
        if not parent:
            return
        # Make sure that parent is not a sibling answer
        item_parent = (parent if not isinstance(parent, DecisionAnswer)
                       else parent.parentItem())
        super(DecisionAnswer, self).insert_symbol(item_parent, x, y)
        self.last_branch_item.connectionBelow = \
                JoinConnection(self.last_branch_item, item_parent)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def set_shape(self, width, height):
        ''' ANSWER has round, disjoint sides - does not fit in a polygon '''
        self.width, self.height = width, height
        point = 20 #width / 2.85
        path = QPainterPath()
        left = QRect(0, 0, point, height)
        right = QRect(width - point, 0, point, height)
        path.arcMoveTo(left, 125)
        path.arcTo(left, 125, 110)
        path.arcMoveTo(right, -55)
        path.arcTo(right, -55, 110)
        path.moveTo(width, height)
        self.setPath(path)
        super(DecisionAnswer, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        return ['ELSE']


# pylint: disable=R0904
class Join(VerticalSymbol):
    ''' JOIN symbol (GOTO) '''
    auto_expand = True
    arrow_head = 'simple'
    common_name = 'terminator_statement'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        self.ast = ast
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super(Join, self).__init__(parent,
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
        super(Join, self).resize_item(rect)

    def set_shape(self, width, height):
        ''' Define the bouding rectangle of the JOIN symbol '''
        circ = min(width, height)
        path = QPainterPath()
        path.addEllipse(0, 0, circ, circ)
        self.setPath(path)
        super(Join, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list - list of labels '''
        return (label.inputString for label in CONTEXT.labels)

    def update_completion_list(self, pr_text):
        ''' When text was entered, update list of join terminators '''
        ast, _, _, _, _ = self.parser.parseSingleElement(self.common_name,
                                                         pr_text)
        for each in (t for t in CONTEXT.terminators if t.kind == 'join'):
            if each.inputString == unicode(self):
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
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super(ProcedureStop, self).__init__(parent, ast)

    def set_shape(self, width, height):
        ''' Define the symbol shape '''
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
        try:
            CONTEXT.state_exitpoints = \
                    set(CONTEXT.state_exitpoints) | set(unicode(self))
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

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Label()
        self.ast = ast
        super(Label, self).__init__(parent,
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
        path = QPainterPath()
        path.addEllipse(0, height / 2, width / 4, height / 2)
        path.moveTo(width / 4, height * 3 / 4)
        path.lineTo(width / 2, height * 3 / 4)
        # Add arrow head
        path.moveTo(width / 2 - 5, height * 3 / 4 - 5)
        path.lineTo(width / 2, height * 3 / 4)
        path.lineTo(width / 2 - 5, height * 3 / 4 + 5)
        # Add vertical line in the middle of the symbol
        path.moveTo(width / 2, 0)
        path.lineTo(width / 2, height)
        # Make sure the bounding rect is withing specifications
        path.moveTo(width, height)
        self.setPath(path)
        super(Label, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list - list of JOIN '''
        return (term.inputString
                for term in CONTEXT.terminators if term.kind == 'join')

    def update_completion_list(self, pr_text):
        ''' When text was entered, update list of labels in current context '''
        ast, _, _, _, _ = self.parser.parseSingleElement(self.common_name,
                                                         pr_text)
        for each in CONTEXT.labels:
            if each.inputString == unicode(self):
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

    def __init__(self, parent=None, ast=None):
        ''' Initializes the TASK symbol '''
        ast = ast or ogAST.Task()
        self.ast = ast
        super(Task, self).__init__(parent,
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
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Task, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        elems = unicode(self).lower().strip().split()
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
                         for name, cty in AST.asn1_constants.viewitems()}
            for name, (asn1ty, _) in chain (CONTEXT.variables.viewitems(),
                                          CONTEXT.global_variables.viewitems(),
                                          constants.viewitems(),
                                          fpar.viewitems()):
                if name == varname:
                    asn1_filter = [asn1ty]
                    break
        return chain(variables_autocompletion(self, asn1_filter),
                     ogParser.SPECIAL_OPERATORS.viewkeys())

# pylint: disable=R0904
class ProcedureCall(VerticalSymbol):
    ''' PROCEDURE CALL symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'procedure_call'
    # Define reserved keywords for the syntax highlighter
    blackbold = ['\\bWRITELN\\b', '\\bWRITE\\b',
                 '\\bSET_TIMER\\b', '\\bRESET_TIMER\\b']
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output(defName='')
        self.ast = ast
        super(ProcedureCall, self).__init__(parent,
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
        path = QPainterPath()
        path.addRect(0, 0, width, height)
        path.moveTo(7, 0)
        path.lineTo(7, height)
        path.moveTo(width - 7, 0)
        path.lineTo(width - 7, height)
        self.setPath(path)
        super(ProcedureCall, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        if '(' in unicode(self):
            # Get the variables of the type of the current parameter
            count = unicode(self).count(',')
            procname = unicode(self).split('(')[0].strip().lower()
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
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, ast=None):
        ''' Create a Text Symbol '''
        ast = ast or ogAST.TextArea()
        self.ast = ast
        super(TextSymbol, self).__init__(parent=None,
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

    def update_completion_list(self, pr_text):
        ''' When text was entered, update list of variables/FPAR/Timers '''
        # Get AST for the symbol
        ast, _, _, _, _ = self.parser.parseSingleElement('text_area', pr_text)
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
        super(TextSymbol, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' Text Symbol only resizes down or right '''
        if self.grabber.resize_mode.endswith('left'):
            return
        self.prepareGeometryChange()
        self.set_shape(rect.width(), rect.height())


class ASN1Viewer(TextSymbol):
    ''' Text symbol with dedicated text highlighting set of words for ASN.1 '''
    blackbold = ['\\b{}\\b'.format(word) for word in (
                 'DEFINITIONS', 'AUTOMATIC', 'TAGS', 'BEGIN', 'END', 'INTEGER',
                 'OCTET', 'STRING', 'BIT', 'REAL', 'SEQUENCE', 'OF', 'WITH',
                 'IMPORTS', 'FROM', 'SIZE', 'CHOICE', 'BOOLEAN', 'ENUMERATED')]


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

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.State()
        self.ast = ast
        ast.inputString = getattr(ast, 'via', None) or ast.inputString
        super(State, self).__init__(parent=parent,
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
        result = not any(elem in unicode(self).lower().strip()
                       for elem in ('-', ',', '*'))
        return result

    @property
    def nested_scene(self):
        ''' Redefined - nested scene per state must be unique '''
        return self._nested_scene

    def double_click(self):
        ''' Catch a double click - Set nested scene '''
        for each, value in self.scene().composite_states.viewitems():
            if unicode(self).split()[0].lower() == unicode(each):
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
        # Get AST for the symbol and update the context dictionnary
        ast, _, _, _, _ = self.parser.parseSingleElement('state', pr_text)
        for each in ast.statelist:
            CONTEXT.mapping[each.lower()] = None

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        elems = unicode(self).lower().strip().split()
        if len(elems) == 2 and elems[1] == 'via':
            # Get list of entry point of the nested state
            statename = elems[0]
            for each in CONTEXT.composite_states:
                if each.statename == statename:
                    return each.state_entrypoints
        else:
            return set(state for state in CONTEXT.mapping if state != 'START')

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, height / 4, height)

        if self.nested_scene and self.is_composite():
            # Distinguish composite states with dash line
            self.setPen(QPen(Qt.DashLine))
        else:
            self.setPen(QPen(Qt.SolidLine))
        self.setPath(path)
        super(State, self).set_shape(width, height)

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
    common_name = 'process_definition'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = True
    arrow_head = 'angle'
    arrow_tail = 'angle'

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Process()
        self.ast = ast
        super(Process, self).__init__(parent=None,
                                      text=ast.processName,
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

    def insert_symbol(self, parent, x, y):
        ''' Redefinition - adds connection line to env '''
        super(Process, self).insert_symbol(parent, x, y)
        if not self.connection:
            self.connection = self.connect_to_parent()

    def connect_to_parent(self):
        ''' Redefinition: creates connection to env with a signalroute '''
        return Signalroute(self)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
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
        super(Process, self).set_shape(width, height)


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

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Procedure()
        self.ast = ast
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

    def update_completion_list(self, **kwargs):
        ''' When text was entered, update completion list of ProcedureCall '''
        for each in CONTEXT.procedures:
            if unicode(self.text).lower() == each.inputString:
                break
        else:
            new_proc = ogAST.Procedure()
            new_proc.inputString = unicode(self.text).lower()
            CONTEXT.procedures.append(new_proc)



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

    def __init__(self, ast=None):
        ''' Create the START symbol '''
        ast = ast or ogAST.Start()
        self.ast = ast
        self.terminal_symbol = False
        super(Start, self).__init__(parent=None,
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

    def __unicode__(self):
        ''' User cannot enter text in the START symbol - Return dummy text '''
        return u'START'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, height / 2, height / 2)
        self.setPath(path)
        super(Start, self).set_shape(width, height)


class ProcedureStart(Start):
    ''' Start symbol of a procedure - only shape differs from Start '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    common_name = 'proc_start'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
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

    def __unicode__(self):
        ''' Return the state entry point '''
        return unicode(self.text)

    def update_completion_list(self, pr_text):
        ''' Update nested state entry points '''
        CONTEXT.state_entrypoints = \
                set(CONTEXT.state_entrypoints) | set(unicode(self))

# pylint: disable=R0904
class ContinuousSignal(HorizontalSymbol):
    ''' " Provided" part below a state - not a enabling condition '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                             'Input', 'Label', 'Connect', 'ContinuousSignal']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'continuous_signal'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        ''' Create the Provided symbol - use no background color '''
        ast = ast or ogAST.ContinuousSignal()
        self.ast = ast
        self.branch_entrypoint = None
        if not ast.pos_y and parent:
            # Make sure the item is placed below its parent
            ast.pos_y = parent.y() + parent.boundingRect().height() + 10
        super(ContinuousSignal, self).__init__(parent, text=ast.inputString,
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
        super(ContinuousSignal, self).insert_symbol(item_parent, x, y)

    def set_shape(self, width, height):
        ''' Define the shape '''
        path = QPainterPath()
        path.moveTo(15, 0)
        path.lineTo(0, height / 2.0)
        path.lineTo(15, height)
        path.moveTo(width - 15, 0)
        path.lineTo(width, height / 2.0)
        path.lineTo(width - 15, height)
        self.setPath(path)
        super(ContinuousSignal, self).set_shape(width, height)

    @property
    def completion_list(self):
        ''' Set auto-completion list '''
        return variables_autocompletion(self, None)


