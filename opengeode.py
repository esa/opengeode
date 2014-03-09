#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=C0302
"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import signal
import sys
import os
import argparse
import logging
import traceback
import re
import code
import pprint
from functools import partial

# Added to please py2exe - NOQA makes flake8 ignore the following lines:
# pylint: disable=W0611
import antlr3  # NOQA
import antlr3.tree  # NOQA
import importlib  # NOQA
import PySide  # NOQA
import PySide.QtCore  # NOQA
import PySide.QtGui  # NOQA
import PySide.QtUiTools  # NOQA
import undoCommands  # NOQA
import sdl92Lexer  # NOQA
import sdl92Parser  # NOQA
import genericSymbols  # NOQA
import sdlSymbols
import PySide.QtXml  # NOQA
import singledispatch # NOQA

#from PySide import phonon

from PySide import QtGui, QtCore
from PySide.QtCore import Qt, QSize, QFile, QIODevice, QRectF, QTimer

from PySide.QtUiTools import QUiLoader
from PySide import QtSvg

from genericSymbols import Symbol, Comment, EditableText, Cornergrabber
from sdlSymbols import(Input, Output, Decision, DecisionAnswer, Task,
        ProcedureCall, TextSymbol, State, Start, Join, Label, Procedure,
        ProcedureStart, ProcedureStop)

# Icons and png files generated from the resource file:
import icons  # NOQA

import AdaGenerator
import ogParser
import ogAST
import Renderer
import Clipboard
import Statechart
import Lander


# Try importing graphviz for the SDL to Statechart converter
# This is optional, as graphviz installation can not be easily
# automated on some platforms by opengeode installation scripts.
try:
    import pygraphviz as dot
    graphviz = True
except ImportError:
    graphviz = False

try:
    import LlvmGenerator
except ImportError:
    # not sure if LLVM is available on the Windows platform
    pass

__all__ = ['opengeode']
__version__ = '0.99'

if hasattr(sys, 'frozen'):
    # Detect if we are running on Windows (py2exe-generated)
    try:
        CUR_DIR = os.path.dirname(unicode
                (sys.executable, sys.getfilesystemencoding()))
    except TypeError:
        CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    else:
        # Redirect stderr to a log file - to avoid py2exe error message
        # that pops up at application closure when app logs errors
        sys.stdout = open('opengeode_stdout.log', 'w')
        sys.stderr = open('opengeode_stderr.log', 'w')
else:
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))


LOG = logging.getLogger(__name__)


# Global handling all top-level elements
# It seems that if we don't keep a global list of these elements
# (START, STATE, and Text symbols)
# they sometimes get destroyed and disappear from the scene.
# As if a GC was deleting these object *even if they belong to the scene*
# (but have no parentItem). Most likely a Qt/Pyside bug.
G_SYMBOLS = set()


# Other Qt bug:
# QGraphicsTextItem don't stand that their parent item (usually an
# SDL symbol) is removed from the scene (scene.removeItem()). It
# provokes segfault when application exits.
# Workaround is to use hide()/show() to make items disappear
# from the scene (when deleted). Seems OK (MP 2013-03-26)

# Lookup table used to configure the context-dependent toolbars
ACTIONS = {
    'process': [Start, State, Input, Task, Decision, DecisionAnswer,
                Output, ProcedureCall, TextSymbol, Comment, Label,
                Join, Procedure],
    'procedure': [ProcedureStart, Task, Decision,
                  DecisionAnswer, Output, ProcedureCall, TextSymbol,
                  Comment, Label, Join, ProcedureStop],
    'statechart': []
}


class Vi_bar(QtGui.QLineEdit, object):
    ''' Line editor for the Vi-like command mode '''
    def __init__(self):
        ''' Create the bar - no need for parent '''
        super(Vi_bar, self).__init__()

    def keyPressEvent(self, key_event):
        ''' Handle key press - in particular Escape '''
        super(Vi_bar, self).keyPressEvent(key_event)
        if key_event.key() == Qt.Key_Escape:
            self.clearFocus()


class File_toolbar(QtGui.QToolBar, object):
    ''' Toolbar with file open, save, etc '''
    def __init__(self, parent):
        ''' Create the toolbar using standard icons '''
        super(File_toolbar, self).__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.new_button = self.addAction(self.style().standardIcon(
            QtGui.QStyle.SP_FileIcon), 'New model')
        self.open_button = self.addAction(self.style().standardIcon(
            QtGui.QStyle.SP_DialogOpenButton), 'Open model')
        self.save_button = self.addAction(self.style().standardIcon(
            QtGui.QStyle.SP_DialogSaveButton), 'Save model')
        self.check_button = self.addAction(self.style().standardIcon(
            QtGui.QStyle.SP_DialogApplyButton), 'Check model')
        self.addSeparator()
        # Up arrow to come back from a subscene (e.g. procedure)
        self.up_button = self.addAction(self.style().standardIcon(
            QtGui.QStyle.SP_ArrowUp), 'Go one level above')
        self.up_button.setEnabled(False)


class Sdl_toolbar(QtGui.QToolBar, object):
    '''
        Toolbar with SDL symbols
        The list of symbols is passed as paramters at creation time ; the class
        looks for icons for the name of the symbols and .png extension.
        The buttons activation is context dependent. Configuration is done
        directly at symbol leval (using the "allowed_followers" property)
    '''
    def __init__(self, parent):
        ''' Create the toolbar, get icons and link actions '''
        super(Sdl_toolbar, self).__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(35, 35))
        self.actions = {}

    def set_actions(self, bar_items):
        ''' Set the acons and actions on the toolbar '''
        self.actions = {}
        self.clear()
        for item in bar_items:
            item_name = item.__name__
            self.actions[item_name] = self.addAction(
                           QtGui.QIcon(':icons/{icon}'.format(
                           icon=item_name.lower() + '.png')), item_name)
        self.update_menu()

    def enable_action(self, action):
        ''' Used as a slot to allow a scene to enable a menu action,
            e.g. if the Start symbol is deleted, the Start button
            shall be activated '''
        self.actions[action].setEnabled(True)

    def disable_action(self, action):
        ''' See description in enable_action '''
        self.actions[action].setEnabled(False)

    def update_menu(self, scene=None):
        ''' Context-dependent enabling/disabling of menu buttons '''
        try:
            selection = list(scene.selected_symbols())
        except AttributeError:
            selection = []
        if not selection:
            # Second chance, check if an item has focus (editable text)
            try:
                selection.append(scene.focusItem().parentItem())
            except AttributeError:
                pass
        if len(selection) > 1:
            # When several items are selected, disable all menu entries
            for _, action in self.actions.viewitems():
                action.setEnabled(False)
        elif not selection:
            # When nothing is selected:
            # activate everything, and when user selects an icon,
            # keep the action on hold until he clicks on the scene
            for action in self.actions.viewkeys():
                self.actions[action].setEnabled(True)

            # Check for singletons (e.g. START symbol)
            try:
                for item in scene.items():
                    try:
                        if item.is_singleton and item.isVisible():
                            self.actions[
                                    item.__class__.__name__].setEnabled(False)
                    except (AttributeError, KeyError) as error:
                        LOG.debug(str(error))
            except AttributeError:
                pass
        else:
            # Only one selected item
            selection, = selection
            for action in self.actions.viewkeys():
                self.actions[action].setEnabled(False)
            for action in selection.allowed_followers:
                try:
                    self.actions[action].setEnabled(True)
                except KeyError:
                    LOG.debug('No menu item for symbol "' + action + '"')


class SDL_Scene(QtGui.QGraphicsScene, object):
    ''' Main graphic scene (canvas) where the user can place SDL symbols '''
    # Signal to be emitted when the scene is left (e.g. UP button)
    scene_left = QtCore.Signal()

    def __init__(self, context='process'):
        ''' Create an SDL Scene for a given context (process or procedure) '''
        super(SDL_Scene, self).__init__()
        self.mode = 'idle'
        self.context = context
        # Configure the action menu
        all_possible_actions = set()
        for action in ACTIONS.viewvalues():
            all_possible_actions |= set(action)
        self.actions = {action.__name__: partial(self.add_symbol, action)
                for action in all_possible_actions}

        # Create a stack for handling undo/redo commands
        # (defined in undoCommands.py)
        self.undo_stack = QtGui.QUndoStack(self)
        # buttonSelected is used to set which symbol to draw
        # on next scene click (see mousePressEvent)
        self.button_selected = None
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QImage(':icons/texture.png')))
        self.messages_window = None
        self.click_coordinates = None
        self.process_name = 'opengeode'
        # search_item/search_pattern are used for search/replace function
        self.search_item = None
        self.search_pattern = None
        # Selection rectangle when user clicks on the scene and moves mouse
        self.select_rect = None

    def quit_scene(self):
        ''' Called in case of scene switch (e.g. UP button) '''
        pass

    def render_process(self, process):
        ''' Render a process and its inner procedures in the scene '''
        self.process_name = process.processName or 'opengeode'
        for top_level in Renderer.render(process, scene=self):
            G_SYMBOLS.add(top_level)
            # Render optional sub-scenes (procedures)
            if top_level.nested_scene:
                subscene = SDL_Scene(
                        context=top_level.__class__.__name__.lower())
                subscene.messages_window = self.messages_window
                for sub_top_level in Renderer.render(
                                       top_level.nested_scene.content,
                                       scene=subscene):
                    G_SYMBOLS.add(sub_top_level)
                top_level.nested_scene = subscene

    def refresh(self):
        ''' Refresh the symbols and connections in the scene '''
        for symbol in self.items():
            try:
                symbol.updateConnectionPointPosition()
                symbol.updateConnectionPoints()
            except AttributeError:
                # Applies only to Symbol instances
                pass
            try:
                # EditableText refreshing - design explanation:
                # The first one is tricky: at symbol initialization,
                # the bounding rect of the text is computed from the raw
                # text value, without any formatting. However, it can
                # happen that text (especially when a model is loaded)
                # contains highlighted data (bold), which has the effect
                # of making the width of the text in fact wider than
                # the bounding rect. The set_text_alignment function,
                # that is applying the aligment of the text within its
                # bounding rect, can work only if the text width is fixed.
                # It has to set it according to the bounding rect, which,
                # therefore can be too small, and this has the effect of
                # pushing the exceeding character to the next line.
                # The only way to avoid this is to call setTextWidth
                # with the value -1 before the aligment is computed.
                # This has the effect of re-computing the bounding rect
                # and fixing the width issue.
                symbol.setTextWidth(-1)
                symbol.set_textbox_position()
                symbol.try_resize()
                symbol.set_text_alignment()
            except AttributeError:
                pass
        for symbol in self.items():
            try:
                symbol.update_connections()
            except AttributeError:
                pass

    def set_cursor(self, follower):
        ''' Set the cursor shape depending on the selected menu item '''
        for item in self.items():
            try:
                if follower.__name__ not in item.allowed_followers:
                    item.setCursor(Qt.ForbiddenCursor)
                else:
                    item.setCursor(Qt.PointingHandCursor)
            except AttributeError:
                # if there are items not having allowed_followers
                pass

    def reset_cursor(self):
        ''' Reset the default cursor of an item '''
        for item in self.items():
            try:
                item.setCursor(item.default_cursor)
            except AttributeError:
                pass

    def selected_symbols(self):
        ''' Generate the list of selected symbols (excluding grabbers) '''
        for selection in self.selectedItems():
            if isinstance(selection, Symbol):
                yield selection
            elif isinstance(selection, Cornergrabber):
                yield selection.parent

    def set_selection(self, toolbar):
        ''' When the selection has changed, update menu, etc '''
        toolbar.update_menu(self)
        for item in self.selected_symbols():
            item.grabber.display()

    def raise_syntax_errors(self, errors=None):
        ''' Display an syntax error pop-up message '''
        if not errors:
            return
        for view in self.views():
            errs = []
            for error in errors:
                split = error.split()
                if split[0] == 'line' and len(split) > 1:
                    line_col = split[1].split(':')
                    if len(line_col) == 2:
                        # Get line number and column..to locate error
                        # line_nb, col = line_col
                        errs.append(' '.join(split[2:]))
                    else:
                        errs.append(error)
                else:
                    errs.append(error)
            self.clear_focus()
            msg_box = QtGui.QMessageBox(view)
            msg_box.setIcon(QtGui.QMessageBox.Warning)
            msg_box.setWindowTitle('OpenGEODE - Syntax Error')
            msg_box.setInformativeText('\n'.join(errs))
            msg_box.setText("Syntax error!")
            msg_box.setStandardButtons(QtGui.QMessageBox.Discard)
            msg_box.setDefaultButton(QtGui.QMessageBox.Discard)
            msg_box.exec_()

    def find_text(self, pattern):
        ''' Return all symbols with matching text '''
        for item in (symbol for symbol in self.items()
                     if isinstance(symbol, EditableText)
                     and symbol.isVisible()):
            if re.search(pattern, str(item), flags=re.IGNORECASE):
                yield item.parentItem()

    def search(self, pattern, replace_with=None):
        ''' Search and replace function ; get next search result with key n '''
        self.clearSelection()
        self.clear_focus()
        if pattern.endswith('\\'):
            # Avoid buggy pattern ending with a single backslash
            pattern += '\\'
        self.search_item = self.find_text(pattern)
        self.search_pattern = pattern
        if replace_with:
            with undoCommands.UndoMacro(self.undo_stack, 'Search and Replace'):
                for item in self.search_item:
                    new_string = re.sub(pattern,
                                        replace_with,
                                        str(item.text),
                                        flags=re.IGNORECASE)
                    undo_cmd = undoCommands.ReplaceText(
                                         item.text, str(item.text), new_string)
                    self.undo_stack.push(undo_cmd)
                    item.select()
            self.refresh()
        else:
            try:
                item = self.search_item.next()
                item.select()
                item.ensureVisible()
            except StopIteration:
                LOG.info('Pattern not found')

    def show_item(self, item):
        '''
            Select an item and make sure it is visible
            (used when user clicks on a warning or error to locate the symbol)
        '''
        abs_coordinates = item.data(Qt.UserRole)
        if not abs_coordinates:
            LOG.info('Corresponding symbol not found')
            return
        item = self.itemAt(*abs_coordinates)
        if item:
            self.clearSelection()
            self.clear_focus()
            item.setSelected(True)
            item.ensureVisible()

    def delete_selected_symbols(self):
        '''
            Remove selected symbols from the scene, with proper re-connections
        '''
        self.undo_stack.beginMacro('Delete items')
        for item in self.selected_symbols():
            if not item.scene():
                # Ignore if item has already been deleted
                # (in case of multiple selection)
                continue
            undo_cmd = undoCommands.DeleteSymbol(item)
            self.undo_stack.push(undo_cmd)
            try:
                item.branchEntryPoint.parent.updateConnectionPointPosition()
                item.branchEntryPoint.parent.updateConnectionPoints()
            except AttributeError:
                pass
        self.undo_stack.endMacro()

    def copy_selected_symbols(self):
        '''
            Create a copy of selected symbols to a buffer (in AST form)
            Called when user presses Ctrl-C
        '''
        self.click_coordinates = None
        try:
            Clipboard.copy(self.selected_symbols())
        except TypeError as error_msg:
            try:
                self.messages_window.addItem(str(error_msg))
            except AttributeError:
                LOG.error(str(error_msg))
            raise

    def cut_selected_symbols(self):
        '''
            Create a copy of selected symbols, then delete them
        '''
        try:
            self.copy_selected_symbols()
        except TypeError:
            LOG.error('Copy error - Cannot cut')
        else:
            self.delete_selected_symbols()

    def paste_symbols(self):
        '''
            Paste previously copied symbols at selection point
        '''
        parent = list(self.selected_symbols())
        if len(parent) > 1:
            self.messages_window.addItem(
                    'Cannot paste when several items are selected')
        else:
            parent_item, = parent or [None]
            try:
                new_items = Clipboard.paste(parent_item, self)
            except TypeError as error_msg:
                self.messages_window.addItem(str(error_msg))
            else:
                self.undo_stack.beginMacro('Paste')
                for item in new_items:
                    # Allow pasting inputs when input is selected
                    # Same for decision answers.
                    if(isinstance(parent_item, genericSymbols.HorizontalSymbol)
                            and type(parent_item) == type(item)):
                        parent_item = parent_item.parentItem()

                    undo_cmd = undoCommands.InsertSymbol(item, parent_item,
                            pos=None if parent_item
                                     else self.click_coordinates or item.pos())

                    self.undo_stack.push(undo_cmd)
                    if parent_item:
                        parent_item = item
                    else:
                        G_SYMBOLS.add(item)
                    item.cam(item.pos(), item.pos())
                self.undo_stack.endMacro()
                self.refresh()

    def get_pr_string(self):
        ''' Parse the graphical items and returns a PR string '''
        pr_data = ['PROCESS ' + self.process_name + ';']
        # Separate the text boxes and START symbol from the states
        # (They need to be placed at the top of the .pr file
        items = [item for item in self.items() if item.isVisible()]
        states = (item for item in items if isinstance(item, State))
        texts = (item for item in items if isinstance(item, TextSymbol))
        procs = (item for item in items if isinstance(item, Procedure))
        start = [item for item in items if isinstance(item, Start)]
        labels = (item for item in items if isinstance(item, Label) and
                not item.hasParent)

        for item in texts:
            pr_data.append(repr(item))
        for item in procs:
            pr_data.append(repr(item))
        try:
            start, = start
            pr_data.append(repr(start))
        except ValueError:
            LOG.debug('START Symbol missing')
        for item in labels:
            pr_data.append(item.parse_gr())
        for item in states:
            pr_data.append(item.parse_gr())
        pr_data.append('ENDPROCESS ' + self.process_name + ';')
        return pr_data

    def sdl_to_statechart(self):
        ''' Create a graphviz representation of the SDL model '''
        graph = dot.AGraph(strict=False, directed=True)
        pr_raw = self.get_pr_string()
        pr_data = str('\n'.join(pr_raw))
        ast, _, ___ = ogParser.parse_pr(string=pr_data)
        process_ast, = ast.processes
        diamond = 0
        for state, inputs in process_ast.mapping.viewitems():
            # create a new node for each state
            if state == 'START':
                graph.add_node(state, shape='point',
                        fixedsize='true', width=10.0 / 72.0)
            else:
                graph.add_node(state, shape='record', style='rounded')
            # Add edges
            transitions = inputs if state != 'START' else [
                                                    process_ast.content.start]
            for trans in transitions:
                source = state
                # transition label - there can be several inputs
                try:
                    # Keep only message name, remove params and newlines
                    # (newlines are not supported by graphviz)
                    label, = re.match(r'([^(]+)',
                                      trans.inputString).groups()
                    label = label.strip().replace('\n', ' ')
                except AttributeError:
                    # START transition has no inputString
                    label = ''

                def find_terminators(trans):
                    ''' Recursively find all NEXTSTATES '''
                    next_states = [term for term in trans.terminators
                            if term.kind == 'next_state']
                    joins = [term for term in trans.terminators
                            if term.kind == 'join']
                    for join in joins:
                        # JOIN - Find corresponding label
                        try:
                            corr_label, = [lab for lab in
                                process_ast.content.floating_labels +
                                process_ast.labels if
                                lab.inputString.lower() ==
                                join.inputString.lower()]
                        except ValueError:
                            LOG.error('Missing label: ' + join.inputString)
                        else:
                            # Don't recurse forever in case of livelock
                            if corr_label.inputString != trans.inputString:
                                next_states.extend(
                                        find_terminators(corr_label))
                    return set(next_states)

                # Determine the list of terminators in this transition
                next_states = find_terminators(trans)

                if len(next_states) > 1:
                    # more than one terminator - add intermediate node
                    graph.add_node(str(diamond), shape='diamond',
                            fixedsize='true',
                            width=15.0 / 72.0, height=15.0 / 72.0, label='')
                    graph.add_edge(source, str(diamond), label=label)
                    source = str(diamond)
                    label = ''
                    diamond += 1
                for term in next_states:
                    if term.inputString.strip() == '-':
                        target = state
                    else:
                        target = term.inputString.lower()
                    LOG.debug('Edge from ' + source + ' to ' +
                            term.inputString + ' label: ' + label)
                    graph.add_edge(source, target, label=label)
        #print graph.to_string()
        return graph


    def export_branch_to_picture(self, symbol, filename, doc_format):
        ''' Save a symbol and its followers to a file '''
        temp_scene = SDL_Scene()
        self.clearSelection()
        symbol.select()
        try:
            self.copy_selected_symbols()
            temp_scene.paste_symbols()
            temp_scene.export_img(filename, doc_format)
        except AttributeError:
            pass


    def export_img(self, filename=None, doc_format='png', split=False):
        ''' Save the scene as a PNG/SVG or PDF document
            If specified, split the diagram in multiple files, one
            per top-level floating item
        '''
        if not filename:
            return

        if split:
            # Save in multiple files
            index = 0
            items = (item for item in self.items()
                    if item.isVisible() and not item.hasParent and
                isinstance(item, (State, TextSymbol, Procedure, Start, Label)))
            for item in items:
                self.export_branch_to_picture(item,
                                              filename + str(index),
                                              doc_format)
                index += 1

        if filename.split('.')[-1] != doc_format:
            filename += '.' + doc_format

        self.clearSelection()
        self.clear_focus()
        old_brush = self.backgroundBrush()
        self.setBackgroundBrush(QtGui.QBrush())
        rect = self.itemsBoundingRect()
        # enlarge the rect to fit extra pixels due to antialiasing
        rect.adjust(-5, -5, 5, 5)
        if doc_format == 'png':
            device = QtGui.QImage(rect.size().toSize(),
                    QtGui.QImage.Format_ARGB32)
            device.fill(Qt.transparent)
        elif doc_format == 'svg':
            device = QtSvg.QSvgGenerator()
            device.setFileName(filename)
            device.setTitle('OpenGEODE SDL Diagram')
            device.setSize(rect.size().toSize())
        elif doc_format == 'pdf':
            device = QtGui.QPrinter()
            device.setOutputFormat(QtGui.QPrinter.PdfFormat)
            device.setPaperSize(
                    rect.size().toSize(), QtGui.QPrinter.Point)
            device.setFullPage(True)
            device.setOutputFileName(filename)
        else:
            LOG.error('Output format not supported: ' + doc_format)
        painter = QtGui.QPainter(device)
        self.render(painter, source=rect)
        try:
            device.save(filename)
        except AttributeError:
            # Due to inconsistencies in Qt API - only QtGui.QImage has the save
            pass
        if painter.isActive():
            painter.end()
        self.setBackgroundBrush(old_brush)

    def clear_focus(self):
        ''' Clear focus from any item on the scene '''
        try:
            self.focusItem().clearFocus()
        except AttributeError:
            # if no focus item
            pass

    def symbol_near(self, pos, dist=5, selectable_only=True):
        ''' If any, returns symbol around pos '''
        items = self.items(
                QRectF(pos.x() - dist, pos.y() - dist, 2 * dist, 2 * dist))
        for item in items:
            if((selectable_only and item.flags() &
                    QtGui.QGraphicsItem.ItemIsSelectable)
                    or not selectable_only):
                return item.parent if isinstance(item, Cornergrabber) else item

    def can_insert(self, pos, item_type):
        ''' Check if we can add an item type at a given position '''
        parent_item = self.symbol_near(pos)
        if not parent_item:
            # No symbol at the given position
            if item_type.needs_parent:
                raise TypeError(str(item_type.__name__) + ' needs a parent')
            else:
                return None
        else:
            # Check if item as pos accepts item type as follower
            if item_type.__name__ in parent_item.allowed_followers:
                return parent_item
            else:
                raise TypeError(parent_item.__class__.__name__ +
                                ' symbol cannot be followed by ' +
                                item_type.__name__)

    # pylint: disable=C0103
    def mousePressEvent(self, event):
        '''
            Handle mouse click on the scene:
            If a symbol was selected in the menu, check if it can be inserted
            Otherwise store the coordinates, in which case if the user does
            a paste action with floating items, they will be placed there.
        '''
        self.reset_cursor()
        # First propagate event to symbols for specific treatment
        super(SDL_Scene, self).mousePressEvent(event)
        # Store mouse coordinates as possible paste position
        self.click_coordinates = event.scenePos()
        # Enter state machine
        if self.mode == 'idle' and event.button() == Qt.LeftButton:
            # Idle mode: click triggers selection square
            nearby_connection = self.symbol_near(event.scenePos(),
                                                 selectable_only=False)
            connection_selected = False
            if isinstance(nearby_connection, genericSymbols.Connection):
                # Click near a connection - forward the event to it
                # (some connections like statechart Edges can react)
                nearby_connection.mousePressEvent(event)
                connection_selected = True
            if not self.symbol_near(event.scenePos(), dist=1):
                self.mode = 'select_items'
                self.orig_pos = event.scenePos()
                self.select_rect = self.addRect(
                        QRectF(self.orig_pos, self.orig_pos))
                if self.context == 'statechart' and not connection_selected:
                    # Specific treatment for statecharts - should subclass
                    for item in self.items():
                        # Remove all Edges control points from the scene
                        try:
                            item.bezier_set_visible(False)
                        except AttributeError:
                            pass

        elif self.mode == 'wait_placement':
            try:
                parent = self.can_insert(
                        event.scenePos(), self.button_selected)
            except TypeError as err:
                self.messages_window.addItem(str(err))
            else:
                with undoCommands.UndoMacro(self.undo_stack, 'Place Symbol'):
                    item = self.place_symbol(
                            item_type=self.button_selected,
                            parent=parent,
                            pos=event.scenePos() if not parent else None)
            # self.button_selected = None
            self.mode = 'idle'
        elif self.mode == 'wait_connection_source':
            # Check location, and if ok:
            self.mode = 'wait_next_connection_point'
            # if not OK, reset and:
            self.mode = 'idle'

    # pylint: disable=C0103
    def mouseMoveEvent(self, event):
        ''' Handle Click + Mouse move, based on the mode '''
        if event.buttons() == Qt.NoButton or self.mode == 'idle':
            return super(SDL_Scene, self).mouseMoveEvent(event)
        elif self.mode == 'select_items':
            rect = QRectF(self.orig_pos, event.scenePos())
            self.select_rect.setRect(rect.normalized())
        elif self.mode == 'wait_next_connection_point':
            # Update the line
            pass

    # pylint: disable=C0103
    def mouseReleaseEvent(self, event):
        if self.mode == 'select_items':
            for item in self.items(self.select_rect.rect().toRect(),
                    mode=Qt.ContainsItemBoundingRect):
                try:
                    item.select()
                except AttributeError:
                    pass
            self.removeItem(self.select_rect)
        self.mode = 'idle'
        super(SDL_Scene, self).mouseReleaseEvent(event)

    # pylint: disable=C0103
    def keyPressEvent(self, event):
        ''' Handle keyboard: Delete, Undo/Redo '''
        super(SDL_Scene, self).keyPressEvent(event)
        if event.matches(QtGui.QKeySequence.Delete) and self.selectedItems():
            self.delete_selected_symbols()
            self.clearSelection()
            self.clear_focus()
        elif event.matches(QtGui.QKeySequence.Undo):
            if not isinstance(self.focusItem(), EditableText):
                LOG.debug('UNDO ' + self.undo_stack.undoText())
                self.undo_stack.undo()
                self.clearSelection()
                self.refresh()
                # Emit a selection change to make sure the toolbar is updated
                # (e.g. when Undoing a Place START symbol)
                self.selectionChanged.emit()
                self.clear_focus()
        elif event.matches(QtGui.QKeySequence.Redo):
            if not isinstance(self.focusItem(), EditableText):
                LOG.debug('REDO ' + self.undo_stack.redoText())
                self.undo_stack.redo()
                self.clearSelection()
                self.refresh()
                self.clear_focus()
                # Emit a selection change to make sure the toolbar is updated
                self.selectionChanged.emit()
        elif event.matches(QtGui.QKeySequence.Copy):
            if not isinstance(self.focusItem(), EditableText):
                try:
                    self.copy_selected_symbols()
                except TypeError:
                    LOG.error('Cannot copy')
        elif event.matches(QtGui.QKeySequence.Cut):
            self.cut_selected_symbols()
        elif event.matches(QtGui.QKeySequence.Paste):
            if not isinstance(self.focusItem(), EditableText):
                self.paste_symbols()
                self.refresh()
                self.clear_focus()
        elif event.key() == Qt.Key_N:
            # n to select the next item in a search (vim mode)
            if self.focusItem():
                # Only active when no item has keyboard focus
                return
            try:
                self.clearSelection()
                item = self.search_item.next()
                item.select()
                item.ensureVisible()
            except StopIteration:
                LOG.info('No more matches')
                self.search(self.search_pattern)
            except AttributeError:
                LOG.info('No search pattern set. Use "/<pattern>"')
        elif (event.key() == Qt.Key_J and
                event.modifiers() == Qt.ControlModifier):
            # Debug mode
            for selection in self.selected_symbols():
                LOG.info(str(selection))
                LOG.info('Position: ' + str(selection.pos()))
                LOG.info('ScenePos: ' + str(selection.scenePos()))
                LOG.info('BoundingRect: ' + str(selection.boundingRect()))
                #LOG.info('ChildrenList: ' + str(selection.childItems()))
                LOG.info('ChildrenBoundingRect: ' +
                        str(selection.childrenBoundingRect()))
                pprint.pprint(selection.__dict__, None, 2, 1)
            code.interact('type your command:', local=locals())

    def place_symbol(self, item_type, parent, pos=None):
        ''' Draw a symbol on the scene '''
        item = item_type()
        # Add the item to the scene
        if item not in self.items():
            self.addItem(item)
        # Create Undo command (makes the call to the insertSymbol function):
        undo_cmd = undoCommands.InsertSymbol(item=item, parent=parent, pos=pos)
        self.undo_stack.push(undo_cmd)
        # If no item is selected (e.g. new STATE), add it to the scene
        if not parent:
            G_SYMBOLS.add(item)

        if item_type == Decision:
            # When creating a new decision, add two default answers
            self.place_symbol(item_type=DecisionAnswer, parent=item)
            self.place_symbol(item_type=DecisionAnswer, parent=item)
        elif item_type == Procedure:
            # Create a sub-scene for the procedure
            subscene = SDL_Scene(context='procedure')
            subscene.messages_window = self.messages_window
            item.nested_scene = subscene

        self.clearSelection()
        self.clear_focus()
        item.select()
        item.cam(item.pos(), item.pos())
        # When item is placed, immediately set focus to input text
        item.edit_text()

        for view in self.views():
            view.viewport().update()
            view.ensureVisible(item)
        return item

    def add_symbol(self, item_type):
        ''' Add a symbol, or postpone until a parent symbol is selected  '''
        try:
            # If an item is selected or if its text has focus,
            # use it as parent item for the newly inserted item
            selection, = (list(self.selected_symbols()) or
                          [self.focusItem().parentItem()])
            with undoCommands.UndoMacro(self.undo_stack, 'Place Symbol'):
                self.place_symbol(item_type=item_type, parent=selection)
        except (ValueError, AttributeError):
            # Menu item clicked but no symbol selected
            # -> store until user clicks on the scene
            self.messages_window.clear()
            self.messages_window.addItem(
                    'Click on the scene to place the symbol')
            self.button_selected = item_type
            if item_type == genericSymbols.Connection:
                self.mode = 'wait_connection_source'
            else:
                self.mode = 'wait_placement'
            self.set_cursor(item_type)
            return None


class SDL_View(QtGui.QGraphicsView, object):
    ''' Main graphic view used to display the SDL scene and handle zoom '''
    def __init__(self, scene):
        ''' Create the SDL view holding the scene '''
        super(SDL_View, self).__init__(scene)
        self.wrapping_window = None
        self.messages_window = None
        self.mode = ''
        self.phantom_rect = None
        self.filename = ''
        self.orig_pos = None
        # mouse_pos is used to handle screen scrolling with middle mouse button
        self.mouse_pos = None
        # Up button allows to move from one scene to another
        self.up_button = None
        # Toolbar with the icons of the SDL symbols
        self.toolbar = None
        # Scene stack (used for nested symbols)
        self.parent_scene = []
        # Set of PR files that are not saved back (e.g. system structure)
        self.readonly_pr = None
        # Special scene for the Lander module
        self.lander_scene = SDL_Scene(context='lander')
        # Do not initialize the lander now - only if needed
        self.lander = None

    def set_toolbar(self):
        ''' Define the toolbar depending on the context '''
        self.toolbar.set_actions(
                bar_items=ACTIONS.get(self.scene().context, []))

        # Connect toolbar actions
        self.scene().selectionChanged.connect(partial(
                                    self.scene().set_selection, self.toolbar))
        for item in self.toolbar.actions.viewkeys():
            self.toolbar.actions[item].triggered.connect(
                                                   self.scene().actions[item])
        self.toolbar.update_menu(self.scene())

    # pylint: disable=C0103
    def keyPressEvent(self, event):
        ''' Handle keyboard: Zoom, open/save diagram, etc. '''
        if event.matches(QtGui.QKeySequence.ZoomOut):
            self.scale(0.8, 0.8)
        elif event.matches(QtGui.QKeySequence.ZoomIn):
            self.scale(1.2, 1.2)
        elif event.matches(QtGui.QKeySequence.Save):
            self.save_diagram()
        elif (event.key() == Qt.Key_G and
                event.modifiers() == Qt.ControlModifier):
            self.generate_ada()
        elif event.key() == Qt.Key_F7:
            self.check_model()
        elif event.key() == Qt.Key_F5:
            self.refresh()
        elif event.matches(QtGui.QKeySequence.Open):
            self.open_diagram()
        elif event.matches(QtGui.QKeySequence.New):
            self.new_diagram()
        elif (event.key() == Qt.Key_F12 and
                event.modifiers() == Qt.ControlModifier and
                self.scene() != self.lander_scene):
            self.lander_scene.setSceneRect(0, 0, self.width(), self.height())
            if not self.lander:
                self.lander = Lander.Lander(self.lander_scene)
            self.parent_scene.append(self.scene())
            self.scene().clear_focus()
            self.setScene(self.lander_scene)
            self.up_button.setEnabled(True)
            self.set_toolbar()
            self.lander.play()
        super(SDL_View, self).keyPressEvent(event)

    def refresh(self):
        ''' Refresh the complete view '''
        self.scene().refresh()
        # Refresh statechart
        if graphviz:
            Statechart.update(self.scene())
        self.setSceneRect(self.scene().sceneRect())
        self.viewport().update()

    # pylint: disable=C0103
    def resizeEvent(self, event):
        '''
           Called by Qt when window is resized
           Make sure that the scene that is displayed is at least
           of the size of the view, by drawing a transparent rectangle
           Otherwise, the scene is centered on the view, with the size
           of its bounding rect. This is nice in theory, except when
           the user wants to place a symbol at an exact position - in
           that case, the automatic centering is not appropriate.
        '''
        LOG.debug('resizing view')
        scene_rect = self.scene().itemsBoundingRect()
        view_size = self.size()
        scene_rect.setWidth(max(scene_rect.width(), view_size.width()))
        scene_rect.setHeight(max(scene_rect.height(), view_size.height()))
        if self.phantom_rect and self.phantom_rect in self.scene().items():
            self.scene().removeItem(self.phantom_rect)
        self.phantom_rect = self.scene().addRect(scene_rect,
                pen=QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        # Hide the rectangle so that it does not collide with the symbols
        self.phantom_rect.hide()
        super(SDL_View, self).resizeEvent(event)

    def about_og(self):
        ''' Display the About dialog '''
        QtGui.QMessageBox.about(self, 'About OpenGEODE',
                'OpenGEODE - a tiny SDL editor for TASTE\n\n'
                'Author: \nMaxime Perrotin'
                '\n\nContact: maxime.perrotin@esa.int\n\n'
                'Coded with Pyside (Python + Qt)\n'
                'and ANTLR 3.1.3 for Python (parser)')

    # pylint: disable=C0103
    def wheelEvent(self, wheelEvent):
        '''
            Catch the mouse Wheel event
        '''
        if wheelEvent.modifiers() == Qt.ControlModifier:
            # Google-Earth zoom mode (Zoom with center on the mouse position)
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
            if wheelEvent.delta() < 0:
                self.scale(0.9, 0.9)
            else:
                self.scale(1.1, 1.1)
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        else:
            return(super(SDL_View, self).wheelEvent(wheelEvent))

    # pylint: disable=C0103
    def mousePressEvent(self, evt):
        '''
            Catch mouse press event to move (when middle button is clicked)
            or to select multiple items
        '''
        # First propagate the click (then scene will receive it first):
        super(SDL_View, self).mousePressEvent(evt)
        self.mouse_pos = evt.pos()
        if evt.button() == Qt.MidButton:
            self.mode = 'moveScreen'

    def go_up(self):
        '''
            When Up button is clicked, go up one scene level
            For example to get out of a procedure definition
        '''
        LOG.debug('GO_UP')
        self.scene().clear_focus()
        # Scene may need to be informed when it is left:
        self.scene().scene_left.emit()
        self.setScene(self.parent_scene.pop())
        self.set_toolbar()
        if not self.parent_scene:
            self.up_button.setEnabled(False)
        self.refresh()

    # pylint: disable=C0103
    def mouseDoubleClickEvent(self, evt):
        ''' Catch a double click - possibly change the scene '''
        super(SDL_View, self).mouseDoubleClickEvent(evt)
        if evt.button() == Qt.LeftButton:
            item = self.scene().symbol_near(self.mapToScene(evt.pos()))
            try:
                if item.nested_scene:
                    if not isinstance(item.nested_scene, SDL_Scene):
                        subscene = SDL_Scene(
                                context=item.__class__.__name__.lower())
                        subscene.messages_window = self.messages_window
                        for top_level in Renderer.render_process(
                                                subscene, item.nested_scene):
                            G_SYMBOLS.add(top_level)
                        item.nested_scene = subscene
                    self.parent_scene.append(self.scene())
                    self.scene().clear_focus()
                    self.setScene(item.nested_scene)
                    self.up_button.setEnabled(True)
                    self.set_toolbar()
                    # Refresh to make sure the resizeEvent is emitted
                    self.refresh()
                else:
                    # Otherwise, double-click edits the item text
                    item.edit_text(self.mapToScene(evt.pos()))
            except AttributeError:
                LOG.debug('Ignoring double click')

    # pylint: disable=C0103
    def mouseMoveEvent(self, evt):
        ''' Handle the screen move when user clicks '''
        if evt.buttons() == Qt.NoButton:
            return super(SDL_View, self).mouseMoveEvent(evt)
        new_pos = evt.pos()
        if self.mode == 'moveScreen':
            diff_x = self.mouse_pos.x() - new_pos.x()
            diff_y = self.mouse_pos.y() - new_pos.y()
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() + diff_x)
            v_scroll.setValue(v_scroll.value() + diff_y)
            self.mouse_pos = new_pos
        else:
            return super(SDL_View, self).mouseMoveEvent(evt)

    # pylint: disable=C0103
    def mouseReleaseEvent(self, evt):
        self.mode = ''
        super(SDL_View, self).mouseReleaseEvent(evt)

    def save_as(self):
        ''' Save As function '''
        self.save_diagram(save_as=True)

    def save_diagram(self, save_as=False, autosave=False):
        ''' Save the diagram to a .pr file '''
        if (not self.filename or save_as) and not autosave:
            self.filename = QtGui.QFileDialog.getSaveFileName(
                    self, "Save model", ".", "SDL Model (*.pr)")[0]
        if self.filename and self.filename.split('.')[-1] != 'pr':
            self.filename += ".pr"
        filename = (
                (self.filename or '_opengeode')
                + '.autosave') if autosave else self.filename
        if not filename and not autosave:
            return False
        else:
            pr_file = QFile(filename)
            pr_file.open(QIODevice.WriteOnly | QIODevice.Text)
            if not autosave:
                self.scene().process_name = ''.join(filename
                        .split(os.path.extsep)[0:-1]).split(os.path.sep)[-1]
                self.wrapping_window.setWindowTitle(
                        'process ' + self.scene().process_name + '[*]')
        # If the current scene is a nested one, save the top parent
        if self.parent_scene:
            scene = self.parent_scene[0]
        else:
            scene = self.scene()
        pr_raw = scene.get_pr_string()
        pr_data = str('\n'.join(pr_raw))
        #LOG.debug(str(pr_data))
        try:
            pr_file.write(pr_data)
            pr_file.close()
            if not autosave:
                self.scene().clear_focus()
                self.scene().undo_stack.setClean()
            else:
                LOG.debug('Auto-saving backup file completed:' + filename)
            return True
        except AttributeError:
            LOG.error('Impossible to save the file')
            return False

    def save_png(self):
        ''' Save the current view as a PNG image '''
        filename = QtGui.QFileDialog.getSaveFileName(
                self, "Save picture", ".", "Image (*.png)")[0]
        self.scene().export_img(filename, doc_format='png')

    def load_file(self, files):
        ''' Parse a PR file and render it on the scene '''
        try:
            ast, warnings, errors = ogParser.parse_pr(files=files)
        except IOError:
            LOG.error('Aborting: could not open or parse input file')
            return
        try:
            process, = ast.processes
            self.filename = process.filename
            self.readonly_pr = ast.pr_files - {self.filename}
        except ValueError:
            LOG.error('Cannot load more than one process at a time')
            return
        LOG.debug('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        self.log_errors(errors, warnings)
        self.scene().render_process(process)
        self.wrapping_window.setWindowTitle('process ' +
                                            self.scene().process_name + '[*]')
        self.refresh()
        self.centerOn(self.sceneRect().topLeft())
        self.scene().undo_stack.clear()
        return ast

    def open_diagram(self):
        ''' Load one or several .pr file and display the state machine '''
        if self.new_diagram():
            filenames, _ = QtGui.QFileDialog.getOpenFileNames(self,
                    "Open model(s)", ".", "SDL model (*.pr)")
            if not filenames:
                return
            else:
                self.load_file(filenames)

    def new_diagram(self):
        ''' If model state is clean, reset current diagram '''
        # FIXME: incomplete check of the cleanliness of the model
        # - must check all subscenes
        if self.scene().undo_stack.isClean():
            is_clean = True
            while self.parent_scene:
                self.go_up()
                if not self.scene().undo_stack.isClean():
                    is_clean = False
        else:
            is_clean = False
        if not is_clean:
            # If changes occured since last save, pop up a window
            msg_box = QtGui.QMessageBox(self)
            msg_box.setWindowTitle('OpenGEODE')
            msg_box.setText("The model has been modified.")
            msg_box.setInformativeText("Do you want to save your changes?")
            msg_box.setStandardButtons(QtGui.QMessageBox.Save |
                    QtGui.QMessageBox.Discard |
                    QtGui.QMessageBox.Cancel)
            msg_box.setDefaultButton(QtGui.QMessageBox.Save)
            ret = msg_box.exec_()
            if ret == QtGui.QMessageBox.Save:
                if not self.save_diagram():
                    return False
            elif ret == QtGui.QMessageBox.Discard:
                pass
            elif ret == QtGui.QMessageBox.Cancel:
                return False
        self.scene().undo_stack.clear()
        self.scene().clear()
        G_SYMBOLS.clear()
        self.scene().process_name = ''
        self.filename = None
        self.readonly_pr = None
        self.wrapping_window.setWindowTitle('process[*]')
        self.set_toolbar()
        return True

    def log_errors(self, errors, warnings):
        ''' Report Error and Warnings on the console and in the log window '''
        if self.messages_window:
            self.messages_window.clear()
        for error in errors:
            if type(error[0]) == list:
                # should be fixed now, CHECKME - NO, NOT FULLY FIXED
                # problem is in decision answers branches
                error[0] = 'Internal error - ' + error[0][0]
            LOG.error(error[0])
            item = QtGui.QListWidgetItem(u'[ERROR] ' + error[0])
            if len(error) == 2:
                item.setData(Qt.UserRole, error[1])
            if self.messages_window:
                self.messages_window.addItem(item)
        for warning in warnings:
            LOG.warning(warning[0])
            item = QtGui.QListWidgetItem(u'[WARNING] ' + warning[0])
            if len(warning) == 2:
                item.setData(Qt.UserRole, warning[1])
            if self.messages_window:
                self.messages_window.addItem(item)
        if not errors and not warnings and self.messages_window:
            self.messages_window.addItem('No errors, no warnings!')

    def check_model(self):
        ''' Parse the model and check for warnings and errors '''
        # If the current scene is a nested one, save the top parent
        if self.parent_scene:
            scene = self.parent_scene[0]
        else:
            scene = self.scene()
        pr_raw = scene.get_pr_string()
        pr_data = str('\n'.join(pr_raw))
        if pr_data:
            _, warnings, errors = ogParser.parse_pr(files=self.readonly_pr,
                                                    string=pr_data)
            self.log_errors(errors, warnings)

    def generate_ada(self):
        ''' Generate Ada code '''
        # If the current scene is a nested one, save the top parent
        if self.parent_scene:
            scene = self.parent_scene[0]
        else:
            scene = self.scene()
        pr_raw = scene.get_pr_string()
        pr_data = str('\n'.join(pr_raw))
        if pr_data:
            ast, warnings, errors = ogParser.parse_pr(files=self.readonly_pr,
                                                      string=pr_data)
            process, = ast.processes
            self.log_errors(errors, warnings)
            if len(errors) > 0:
                self.messages_window.addItem(
                        'Aborting: too many errors to generate code')
            else:
                self.messages_window.addItem('Generating Ada code')
                try:
                    AdaGenerator.generate(process)
                    self.messages_window.addItem('Done')
                except (TypeError, ValueError, NameError) as err:
                    self.messages_window.addItem(
                            'Code generation failed:' + str(err))
                    LOG.error(str(traceback.format_exc()))


class OG_MainWindow(QtGui.QMainWindow, object):
    ''' Main GUI window '''
    def __init__(self, parent=None):
        ''' Create the main window '''
        super(OG_MainWindow, self).__init__(parent)
        self.view = None
        self.scene = None
        self.statechart_view = None
        self.statechart_scene = None
        self.vi_bar = Vi_bar()

    def start(self, file_name):
        ''' Initializes all objects to start the application '''
        # Create a graphic scene: the main canvas
        self.scene = SDL_Scene(context='process')
        # Find SDL_View widget
        self.view = self.findChild(SDL_View, 'graphicsView')
        self.view.setScene(self.scene)

        # Find Menu Actions
        open_action = self.findChild(QtGui.QAction, 'actionOpen')
        new_action = self.findChild(QtGui.QAction, 'actionNew')
        save_action = self.findChild(QtGui.QAction, 'actionSave')
        save_as_action = self.findChild(QtGui.QAction, 'actionSaveAs')
        quit_action = self.findChild(QtGui.QAction, 'actionQuit')
        check_action = self.findChild(QtGui.QAction, 'actionCheck_model')
        about_action = self.findChild(QtGui.QAction, 'actionAbout')
        ada_action = self.findChild(QtGui.QAction, 'actionGenerate_Ada_code')
        png_action = self.findChild(QtGui.QAction, 'actionExport_to_PNG')

        # Connect menu actions
        open_action.activated.connect(self.view.open_diagram)
        save_action.activated.connect(self.view.save_diagram)
        save_as_action.activated.connect(self.view.save_as)
        quit_action.activated.connect(self.close)
        new_action.activated.connect(self.view.new_diagram)
        check_action.activated.connect(self.view.check_model)
        about_action.activated.connect(self.view.about_og)
        ada_action.activated.connect(self.view.generate_ada)
        png_action.activated.connect(self.view.save_png)

        # Add a toolbar widget (not in .ui file due to pyside bugs)
        toolbar = Sdl_toolbar(self)

        # Associate the toolbar to the scene
        self.view.toolbar = toolbar

        # Set initial toolbar to the PROCESS editor
        self.view.set_toolbar()

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Add a toolbar with New/Open/Save/Check buttons
        filebar = File_toolbar(self)
        filebar.open_button.activated.connect(self.view.open_diagram)
        filebar.new_button.activated.connect(self.view.new_diagram)
        filebar.check_button.activated.connect(self.view.check_model)
        filebar.save_button.activated.connect(self.view.save_diagram)
        self.view.up_button = filebar.up_button
        filebar.up_button.activated.connect(self.view.go_up)
        self.addToolBar(Qt.TopToolBarArea, filebar)

        self.scene.clearSelection()
        self.scene.clear_focus()

        # widget wrapping the view. We have to maximize it
        process_widget = self.findChild(QtGui.QWidget, 'process')
        process_widget.showMaximized()
        self.view.wrapping_window = process_widget
        self.scene.undo_stack.cleanChanged.connect(
                lambda x: process_widget.setWindowModified(not x))

        # get the messages list window (to display errors and warnings)
        # it is a QtGui.QListWidget
        msg_dock = self.findChild(QtGui.QDockWidget, 'msgDock')
        msg_dock.setWindowTitle('Use F7 to check the model')
        msg_dock.setStyleSheet('QDockWidget::title {background: lightgrey;}')
        messages = self.findChild(QtGui.QListWidget, 'messages')
        messages.addItem('Welcome to OpenGEODE.')
        self.view.messages_window = messages
        self.scene.messages_window = messages
        messages.itemClicked.connect(self.scene.show_item)

        statechart_dock = self.findChild(QtGui.QDockWidget, 'statechart_dock')
        #statechart_dock.setWindowTitle('Statechart view - F4 to update')
        if graphviz:
            self.statechart_view = self.findChild(SDL_View, 'statechart_view')
            self.statechart_scene = SDL_Scene(context='statechart')
            self.statechart_view.setScene(self.statechart_scene)
        else:
            statechart_dock.hide()

        # Set up the dock area to display the ASN.1 Data model
        asn1_dock = self.findChild(QtGui.QDockWidget, 'datatypes_dock' )
        self.datatypes_view = self.findChild(SDL_View, 'datatypes_view')
        self.datatypes_scene = SDL_Scene(context='process')
        self.datatypes_view.setScene(self.datatypes_scene)
        self.asn1_area = sdlSymbols.ASN1Viewer()
        self.asn1_area.text.setPlainText('-- ASN.1 Data Types')
        self.asn1_area.text.try_resize()

        self.datatypes_scene.addItem(self.asn1_area)

        # Create a timer for periodically saving a backup of the model
        autosave = QTimer(self)
        autosave.timeout.connect(
                partial(self.view.save_diagram, autosave=True))
        autosave.start(60000)

        # Add a line editor on the status bar for the vim mode
        self.statusBar().addPermanentWidget(self.vi_bar)
        self.vi_bar.hide()
        self.vi_bar.editingFinished.connect(self.vi_bar.hide)
        self.vi_bar.returnPressed.connect(self.vi_command)

        # Display the view and the scene (allows size() to be up to date)
        self.show()

        if file_name:
            types = []
            ast = self.view.load_file(file_name)
            # Update the dock widget with ASN.1 files content
            try:
                for asn1file in ast.asn1_filenames:
                    with open(asn1file, 'r') as file_handler:
                        types.append('-- ' + asn1file)
                        types.append(file_handler.read())
                if types:
                    self.asn1_area.text.setPlainText('\n'.join(types))
                    self.asn1_area.text.try_resize()
            except IOError as err:
                LOG.warning('ASN.1 file(s) could not be loaded : ' + str(err))
            except AttributeError:
                LOG.warning('No AST, check input files')

    def vi_command(self):
        '''
            Process a vi command as entered in the Vi command line
            Supported commands:
            :<w><q><!> (save, quit)
            /<search pattern>
            :%s/<search_patten>/<replace_with>/g
        '''
        command = self.vi_bar.text()
        # Match vi-like search and replace pattern (e.g. :%s,a,b,g)
        search = re.compile(r':%s(.)(.*)\1(.*)\1(.)')
        try:
            _, pattern, new, ___ = search.match(command).groups()
            LOG.debug('Replacing {this} with {that}'
                          .format(this=pattern, that=new))
            self.scene.search(pattern, replace_with=new)
        except AttributeError:
            if command.startswith('/') and len(command) > 1:
                LOG.debug('Searching for ' + command[1:])
                self.scene.search(command[1:])
            else:
                saveclose = re.compile(r':(w)?(q)?(!)?')
                try:
                    save, close_app, force = saveclose.match(command).groups()
                    if save:
                        saved = self.view.save_diagram()
                        if not saved and not force and close_app:
                            return
                    if force and close_app:
                        self.scene.undo_stack.clear()
                    if close_app:
                        self.close()
                except AttributeError:
                    pass

    # pylint: disable=C0103
    def keyPressEvent(self, key_event):
        ''' Handle keyboard: Statechart rendering '''
        if key_event.key() == Qt.Key_F4 and graphviz:
            graph = self.scene.sdl_to_statechart()
            try:
                Statechart.render_statechart(self.statechart_scene, graph)
            except (IOError, TypeError) as err:
                LOG.debug(str(err))
        elif key_event.key() == Qt.Key_Colon:
            self.vi_bar.show()
            self.vi_bar.setFocus()
            self.vi_bar.setText(':')
        elif key_event.key() == Qt.Key_Slash:
            self.vi_bar.show()
            self.vi_bar.setFocus()
            self.vi_bar.setText('/')
        super(OG_MainWindow, self).keyPressEvent(key_event)

    # pylint: disable=C0103
    def closeEvent(self, event):
        ''' Close main application '''
        if self.view.new_diagram():
            # Clear the list of top-level symbols to avoid possible exit-crash
            # due to pyside badly handling items that are not part of any scene
            G_SYMBOLS.clear()
            # Also clear undo stack that may keep reference to items
            self.scene.undo_stack.clear()
            LOG.debug('Bye bye!')
            super(OG_MainWindow, self).closeEvent(event)
        else:
            event.ignore()


def opengeode():
    ''' Tool entry point '''
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Initialize logging
    terminal_formatter = logging.Formatter(
            fmt="[%(levelname)s] %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(terminal_formatter)
    LOG.addHandler(handler_console)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('OpenGEODE')
    app.setWindowIcon(QtGui.QIcon(':icons/input.png'))

    # Bypass system-default font, to harmonize size on all platforms
    font_database = QtGui.QFontDatabase()
    font_database.addApplicationFont(':fonts/Ubuntu-RI.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-R.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-B.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-BI.ttf')
    app.setFont(QtGui.QFont('Ubuntu', 10))

    # Parse the command line
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument('-g', '--debug', action='store_true', default=False,
            help='Display debug information')
    parser.add_argument('--check', action='store_true', dest='check',
            help='Check a .pr file for syntax and semantics')
    parser.add_argument('--toAda', dest='toAda', action='store_true',
            help='Generate Ada code for the .pr file')
    parser.add_argument('--llvm', dest='llvm', action='store_true',
            help='Generate LLVM IR code for the .pr file (experimental)')
    parser.add_argument('--png', dest='png', action='store_true',
            help='Generate a PNG file for the process')
    parser.add_argument('--pdf', dest='pdf', action='store_true',
            help='Generate a PDF file for the process')
    parser.add_argument('--svg', dest='svg', action='store_true',
            help='Generate a SVG file for the process')
    parser.add_argument('--split', dest='split', action='store_true',
            help='Save pictures in multiple files (one per floating item)')
    parser.add_argument('files', metavar='file.pr', type=str, nargs='*',
                   help='SDL file(s)')
    options = parser.parse_args()
    ret = 0
    if options.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Set log level for all libraries
    LOG.setLevel(level)
    for module in (sdlSymbols, genericSymbols, ogAST, ogParser, Lander,
            AdaGenerator, undoCommands, Renderer, Clipboard, Statechart):
        module.LOG.addHandler(handler_console)
        module.LOG.setLevel(level)

    # Initialize the clipboard
    Clipboard.CLIPBOARD = QtGui.QGraphicsScene()

    LOG.debug('Starting OpenGEODE version ' + __version__)

    if(options.check or options.toAda or options.png or
            options.pdf or options.svg):
        LOG.info('Checking ' + str(options.files))
        try:
            ast, warnings, errors = ogParser.parse_pr(files=options.files)
        except IOError:
            LOG.error('Aborting due to parsing error (check input file)')
            return(-1)
        try:
            process, = ast.processes
        except ValueError:
            LOG.error('Only one process at a time is supported')
            return(-1)
        LOG.info('Parsing complete. Summary, found ' +
                str(len(warnings)) +
                ' warnings and ' +
                str(len(errors)) +
                ' errors')
        for warning in warnings:
            LOG.warning(warning[0])
        for error in errors:
            LOG.error(error[0])
        if len(errors) > 0:
            ret = -1
        if options.toAda:
            if len(errors) > 0:
                LOG.error('Too many errors, cannot generate Ada code')
            else:
                LOG.info('Generating Ada code')
                try:
                    AdaGenerator.generate(process)
                    if options.llvm:
                        # Experimental: generate LLVM IR code
                        LlvmGenerator.generate(process)
                except (TypeError, ValueError, NameError) as err:
                    LOG.error(str(err))
                    print(str(traceback.format_exc()))
                    LOG.error('Code generation failed')
        export_fmt = []
        if options.png:
            export_fmt.append('png')
        if options.pdf:
            export_fmt.append('pdf')
        if options.svg:
            export_fmt.append('svg')
        if export_fmt:
            scene = SDL_Scene(context='process')
            scene.render_process(process)
            # Update connections, placements:
            scene.refresh()
            for doc_fmt in export_fmt:
                LOG.info('Saving {ext} file: {name}.{ext}'.format(
                               ext=doc_fmt, name=process.processName))
                scene.export_img(process.processName,
                                 doc_format=doc_fmt,
                                 split=options.split)
    else:
        LOG.debug('Running the GUI')
        LOG.info('Model backup enabled - auto-saving every 2 minutes')
        # Load the application layout from the .ui file
        loader = QUiLoader()
        loader.registerCustomWidget(OG_MainWindow)
        loader.registerCustomWidget(SDL_View)
        ui_file = QFile(':/opengeode.ui')
        ui_file.open(QFile.ReadOnly)
        my_widget = loader.load(ui_file)
        ui_file.close()
        my_widget.start(options.files)
        ret = app.exec_()
    return(ret)

if __name__ == '__main__':
    sys.exit(opengeode())
