#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0302
"""
    OpenGEODE - TASTE SDL and Observers Editor

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2022 Maxime Perrotin & European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import signal
import sys
import os
import argparse
import logging
import traceback
import ctypes
import re
import code
import pprint
import random
import faulthandler
from functools import partial
from itertools import chain
from importlib import reload

# To freeze the application on Windows, all modules must be imported even
# when they are not directly used from this module (py2exe bug)
# NOQA makes flake8 ignore locally-unused modules
# pylint: disable=W0611
import enum  # NOQA
import string  # NOQA
import fnmatch  # NOQA
import operator  # NOQA
import subprocess  # NOQA
import distutils  # NOQA
import tempfile  # NOQA
import uuid  # NOQA
import importlib  # NOQA
import antlr3  # NOQA
import antlr3.tree  # NOQA
import importlib  # NOQA
from functools import singledispatch

from . import(undoCommands,  # NOQA
              sdl92Lexer,  # NOQA
              sdl92Parser,  # NOQA
              genericSymbols,  # NOQA
              Asn1scc,  # NOQA
              sdlSymbols,
              AdaGenerator,
              ogParser,
              ogAST,
              Renderer,
              Clipboard,
              Statechart,
              Lander,
              Helper,
              Pr,
              CGenerator,
              Connectors,  # NOQA
              TextInteraction)  # NOQA
import pygraphviz  # NOQA
from typing import List, Union, Dict, Set, Any, Tuple


from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import *
from PySide6 import QtSvg

from .genericSymbols import Symbol, Comment, Cornergrabber, Connection, Channel
from .sdlSymbols import(Input,
                        Output,
                        Decision,
                        DecisionAnswer,
                        Task,
                        ProcedureCall,
                        TextSymbol,
                        State,
                        Start,
                        Join,
                        Label,
                        Procedure,
                        ProcedureStart,
                        ProcedureStop,
                        StateStart,
                        Connect,
                        Process,
                        ContinuousSignal,
                        ProcessType)

from .TextInteraction import EditableText

from .sdlHelp import OG_HelpBrowser

# Icons and png files generated from the resource file:
from . import icons  # NOQA

# Logging: ist of properly loaded modules that will use it
LOG = logging.getLogger(__name__)
MODULES = [
    sdlSymbols,
    genericSymbols,
    ogAST,
    ogParser,
    Lander,
    AdaGenerator,
    undoCommands,
    Renderer,
    Clipboard,
    Statechart,
    Helper,
    Asn1scc,
    Connectors,
    Pr,
    TextInteraction,
    Connectors,
    CGenerator,
] # type: List[module]

# Define custom UserRoles
ANCHOR = Qt.UserRole + 1

try:
    import LlvmGenerator
    MODULES.append(LlvmGenerator)
except ImportError:
    pass

try:
    import StgBackend
    MODULES.append(StgBackend)
except ImportError:
    pass


__all__ = ['opengeode', 'SDL_Scene', 'SDL_View', 'parse']
__version__ = '3.9.30'

if hasattr(sys, 'frozen'):
    # Detect if we are running on Windows (py2exe-generated)
    try:
        CUR_DIR = os.path.dirname(
                str(sys.executable, sys.getfilesystemencoding()))
    except TypeError:
        CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    else:
        # Redirect stderr to a log file - to avoid py2exe error message
        # that pops up at application closure when app logs errors
        sys.stdout = open('opengeode_stdout.log', 'w')
        sys.stderr = open('opengeode_stderr.log', 'w')
else:
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))


# Global handling all top-level elements
# It seems that if we don't keep a global list of these elements
# (START, STATE, and Text symbols)
# they sometimes get destroyed and disappear from the scene.
# As if a GC was deleting these object *even if they belong to the scene*
# (but have no parentItem). Most likely a Qt/Pyside bug.
# NOTE: This was not re-evaluated with PySide6
G_SYMBOLS = set()

# There is a bug in Pyside2 with the setData(..) function. It should
# normally allow to store any type (as QVariant does in C++), however
# it does not manage to store QGraphicsItems (i.e. symbols). Because
# of that we must keep a table to find symbols that contain an error
# The table is cleared each time the Check Model is called
G_ERRORS = list()


# Other Qt bug:
# QGraphicsTextItem don't stand that their parent item (usually an
# SDL symbol) is removed from the scene (scene.removeItem()). It
# provokes segfault when application exits.
# Workaround is to use hide()/show() to make items disappear
# from the scene (when deleted). Seems OK (MP 2013-03-26)

# Lookup table used to configure the context-dependent toolbars
ACTIONS = {
    'block': [Process, ProcessType, Comment, TextSymbol],
    'process': [Start, State, Input, Connect, ContinuousSignal, Task, Decision,
                DecisionAnswer, Output, ProcedureCall, TextSymbol, Comment,
                Label, Join, Procedure],
    'procedure': [ProcedureStart, Task, Decision,
                  DecisionAnswer, Output, ProcedureCall, TextSymbol,
                  Comment, Label, Join, ProcedureStop],
    'statechart': [],
    'state': [StateStart, State, Input, Connect, ContinuousSignal, Task,
              Decision, DecisionAnswer, Output, ProcedureCall, TextSymbol,
              Comment, Label, Join, ProcedureStop, Procedure],
    'clipboard': [Start, State, Input, Connect, Task, Decision, DecisionAnswer,
                  Output, ProcedureCall, TextSymbol, Comment, Label,
                  Join, Procedure, Process, StateStart, ProcedureStop,
                  ContinuousSignal],
    'lander': [],
    'asn1': []
}


def log_errors(window, errors, warnings, clearfirst=True):
    ''' Report Error and Warnings on the console and in the log window '''
    G_ERRORS.clear()
    if window and clearfirst:
        window.clear()
    for error in errors:
        if type(error[0]) == list:
            # should be fixed now, CHECKME - NO, NOT FULLY FIXED
            # problem is in decision answers branches
            error[0] = 'Internal error - ' + str(error[0])
        LOG.error(error[0])
        item = QListWidgetItem('[ERROR] ' + error[0])
        if len(error) == 3:
            item.setData(Qt.UserRole, error[1])
            item.setData(Qt.UserRole + 1, error[2])
        if window:
            window.addItem(item)
    for warning in warnings:
        LOG.warning(warning[0])
        item = QListWidgetItem('[WARNING] ' + str(warning[0]))
        if len(warning) == 3:
            item.setData(Qt.UserRole, warning[1])
            item.setData(Qt.UserRole + 1, warning[2])
        if window:
            window.addItem(item)
    if not errors and not warnings and window:
        window.addItem('No errors, no warnings!')
    if window:
        window.addItem("Error checking complete")


class Vi_bar(QLineEdit, object):
    ''' Line editor for the Vi-like command mode '''
    def __init__(self):
        ''' Create the bar - no need for parent '''
        super().__init__()
        self.history = []
        self.pointer = 0

    def keyPressEvent(self, key_event):
        ''' Handle key press - Escape, command history '''
        super().keyPressEvent(key_event)
        if key_event.key() == Qt.Key_Escape:
            self.clearFocus()
            self.pointer = len(self.history)
        elif key_event.key() == Qt.Key_Return:
            self.history.append(self.text())
            self.pointer = len(self.history)
        elif key_event.key() == Qt.Key_Up:
            if self.text() and self.text() not in self.history:
                self.history.insert(self.pointer + 1, self.text())
            self.pointer = max(0, self.pointer - 1)
            try:
                self.setText(self.history[self.pointer])
            except IndexError as err:
                pass
        elif key_event.key() == Qt.Key_Down:
            self.pointer = min(len(self.history), self.pointer + 1)
            try:
                self.setText(self.history[self.pointer])
            except IndexError:
                pass
            pass


class File_toolbar(QToolBar, object):
    ''' Toolbar with file open, save, etc '''
    def __init__(self, parent):
        ''' Create the toolbar using standard icons '''
        super().__init__(parent)
        self.setObjectName("File Toolbar")  # needed to save geometry
        self.setMovable(False)
        self.setFloatable(False)
        self.new_button = self.addAction(self.style().standardIcon(
            QStyle.SP_FileIcon), 'New model')
        self.open_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogOpenButton), 'Open model')
        self.save_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogSaveButton), 'Save model')
        self.check_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogApplyButton), 'Check model')
        self.addSeparator()
        # Up arrow to come back from a subscene (e.g. procedure)
        self.up_button = self.addAction(self.style().standardIcon(
            QStyle.SP_ArrowUp), 'Go one level above')
        self.up_button.setEnabled(False)


class Sdl_toolbar(QToolBar, object):
    '''
        Toolbar with SDL symbols
        The list of symbols is passed as parameters at creation time ; the class
        looks for icons for the name of the symbols and .png extension.
        The buttons activation is context dependent. Configuration is done
        directly at symbol level (using the "allowed_followers" property)
    '''
    def __init__(self, parent):
        ''' Create the toolbar, get icons and link actions '''
        super().__init__(parent)
        self.setObjectName("SDL Toolbar")  # needed to save geometry
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(35, 35))
        self.actions = {}

    def set_actions(self, bar_items):
        ''' Set the icons and actions on the toolbar '''
        self.actions = {}
        self.clear()
        for item in bar_items:
            item_name = item.__name__
            self.actions[item_name] = self.addAction(
                           QIcon(':icons/{}.png'
                                       .format(item_name.lower())), item_name)
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
            selection = list(scene.selected_symbols)
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
            for _, action in self.actions.items():
                action.setEnabled(False)
        elif not selection:
            # When nothing is selected:
            # activate everything, and when user selects an icon,
            # keep the action on hold until he clicks on the scene
            for action in self.actions.keys():
                self.actions[action].setEnabled(True)

            # Check for singletons (e.g. START symbol)
            try:
                for item in scene.visible_symb:
                    try:
                        if item.is_singleton:
                            self.actions[
                                    item.__class__.__name__].setEnabled(False)
                    except (AttributeError, KeyError) as error:
                        LOG.debug(str(error))
            except AttributeError:
                pass
        else:
            # Only one selected item
            selection, = selection
            for action in self.actions.keys():
                self.actions[action].setEnabled(False)
            for action in getattr(selection, 'allowed_followers', []):
                try:
                    self.actions[action].setEnabled(True)
                except KeyError:
                    pass
                    #LOG.debug('No menu item for symbol "' + action + '"')


class SDL_Scene(QGraphicsScene):
    ''' Main graphic scene (canvas) where the user can place SDL symbols '''
    # Signal to be emitted when the scene is left (e.g. UP button)
    scene_left = Signal()
    context_change = Signal()
    word_under_cursor = Signal(str)

    def __init__(self, context='process', readonly=False):
        ''' Create a Scene for a given context:
            process, procedure, composite state, clipboard, etc.
            Design note: creating subclasses per context was evaluated but
            rejected - there are too few behavioural differences between them
            Creating tons of files / classes is not right. Keep it simple.
            "readonly" is a command line argument that allows to prevent some
            scenes to be modified by the user.
        '''
        super().__init__()
        # Reference to the parent scene
        self.parent_scene = None
        # mode can be "idle", "wait_connection_source", "select_items",
        # "wait_next_connection_point", "wait_placement"
        self.mode = 'idle'
        self.context = context
        self.allowed_symbols = ACTIONS[context]
        self.readonly = readonly
        self.set_readonly(readonly)
        # Configure the action menu
        all_possible_actions = set()
        for action in ACTIONS.values():
            all_possible_actions |= set(action)
        self.actions = {action.__name__: partial(self.add_symbol, action)
                for action in all_possible_actions}

        # Create a stack for handling undo/redo commands
        # (defined in undoCommands.py)
        self.undo_stack = QUndoStack(self)
        # buttonSelected is used to set which symbol to draw
        # on next scene click (see mousePressEvent)
        self.button_selected = None
        self.setBackgroundBrush(QBrush(QImage(':icons/texture.png')))
        self.messages_window = QListWidget()  # default
        self.click_coordinates = None
        self.orig_pos = None
        # When connecting symbols, store list of intermediate points
        self.edge_points = []   # type is List[QPointF] in scene coordinates
        self.temp_lines = []    # type is List[QGraphicsLineItem]
        self.process_name = 'opengeode'
        # Scene name is used to update the tab window name when scene changes
        self.name = ''
        # search_item/search_pattern are used for search/replace function
        self.search_item = None
        self.search_pattern = None
        # Selection rectangle when user clicks on the scene and moves mouse
        self.select_rect = None
        # Keep a list of composite states: {'stateName': SDL_Scene}
        self._composite_states = {}
        # Keep a track of highlighted symbols: { symbol: brush }
        self.highlighted = {}
        self.refresh_requested = False
        # Flag indicating the presence of unsolved semantic errors in the model
        self.semantic_errors = False
        # AST of the parsed scene (updated when the model is checked)
        self.ast = None

    def close(self):
        ''' close function is needed by py.test-qt '''
        pass

    def set_readonly(self, readonly=True):
        ''' Set the current scene as read-only, discard all new actions '''
        if self.context == 'process' and readonly:
            # only applies to 1st level hierarchy (process) allowing to have
            # unmodifiable list of DCL and STATES at the 1st level of hierarchy
            ACTIONS[self.context] = []

    def is_aggregation(self):
        ''' Determine if the current scene is a state aggregation, i.e. if
        if contains only floating states without children
        '''
        for each in self.visible_symb:
            if each.hasParent:
                return False
            if not isinstance(each, State):
                # At the moment do not support Text Areas
                return False
            if any(child for child in each.childSymbols()
                    if isinstance(child, (Input, ContinuousSignal))):
                return False
        return True


    @property
    def visible_symb(self):
        ''' Return the visible items of a scene '''
        return (it for it in self.items() if it.isVisible() and
                isinstance(it, Symbol))


    @property
    def editable_texts(self):
        ''' Return all EditableText areas of a scene '''
        return (it for it in self.items() if it.isVisible() and
                isinstance(it, EditableText))


    @property
    def floating_symb(self):
        ''' Return the top level floating items of a scene '''
        return (it for it in self.visible_symb if not it.hasParent)


    @property
    def processes(self):
        ''' Return visible processes components of the scene '''
        return (it for it in self.visible_symb
                if (isinstance(it, Process) and not isinstance(it, Procedure))
                or isinstance(it, ProcessType))


    @property
    def procedures(self):
        ''' Return visible procedures components of the scene '''
        return (it for it in self.visible_symb if isinstance(it, Procedure))


    @property
    def states(self):
        ''' Return visible state components of the scene '''
        return (it for it in self.visible_symb if isinstance(it, State))


    @property
    def texts(self):
        ''' Return visible text areas components of the scene '''
        return (it for it in self.visible_symb if isinstance(it, TextSymbol))


    @property
    def procs(self):
        ''' Return visible procedure declaration components of the scene '''
        return (it for it in self.visible_symb if isinstance(it, Procedure))


    @property
    def start(self):
        ''' Return visible start components of the scene '''
        return (it for it in self.visible_symb if isinstance(it, Start))


    @property
    def floating_labels(self):
        ''' Return visible floating label components of the scene '''
        return (it for it in self.floating_symb if isinstance(it, Label))


    @property
    def returns(self):
        ''' Return visible return components of the scene '''
        return (it for it in self.visible_symb if isinstance(it,
                                                              ProcedureStop))


    @property
    def composite_states(self):
        ''' Return states that contain a composite part '''
        # Update the list first
        for each in self.states:
            if each.is_composite() and \
                  each.nested_scene not in self._composite_states.values():
                self._composite_states[str(each).split()[0].lower()] = \
                                                            each.nested_scene
        return self._composite_states


    @composite_states.setter
    def composite_states(self, value):
        ''' Attribute setter '''
        self._composite_states = value


    @property
    def all_nested_scenes(self):
        ''' Return all nested scenes, recursively '''
        for each in self.visible_symb:
            if each.nested_scene and isinstance(each.nested_scene, SDL_Scene):
                yield each.nested_scene
                for sub in each.nested_scene.all_nested_scenes:
                    yield sub


    @property
    def path(self):
        ''' Get the path to the current scene as a list
        e.g. ['BLOCK a', 'PROCESS b', ...]
        '''
        if not self.parent_scene:
            return [self.name[0:-3]]
        return self.parent_scene.path + [self.name[0:-3]]


    @property
    def selected_symbols(self):
        ''' Generate the list of selected symbols (excluding grabbers) '''
        for selection in self.selectedItems():
            if isinstance(selection, Symbol):
                yield selection
            elif isinstance(selection, Cornergrabber):
                yield selection.parent


    def quit_scene(self):
        ''' Called in case of scene switch (e.g. UP button) '''
        pass


    def render_everything(self, ast):
        ''' Render a process and its children scenes, recursively '''
        already_created = []
        import timeit

        def recursive_render(content, dest_scene):
            ''' Process the rendering in scenes and nested scenes '''
            if isinstance(content, ogAST.Process):
                # XXX - should be set when entering the process
                self.process_name = ast.processName

            try:
                # Render top-level items and their children:
                for each in Renderer.render(content, dest_scene):
                    G_SYMBOLS.add(each)

                # find errors in the scene
                for s in dest_scene.visible_symb:
                    try:
                        if s.ast.errors or s.ast.warnings:
                            # Keep track of all symbols containing errors,
                            # they are processed in "find_symbols_and_update_errors"
                            G_ERRORS.append(s)
                    except Exception as e:
                        print("Oops", str(e))
                # Refreshing the scene may result in resizing some symbols
                dest_scene.refresh()
                # Once everything is rendered, adjust position of each
                # symbol to the value from the AST (positions may be
                # slightly altered by the reshaping functions)
                def fix_pos_from_ast(symbol):
                    try:
                        if(symbol.ast.pos_x is not None
                                and symbol.ast.pos_y is not None):
                            relpos = symbol.mapFromScene(symbol.ast.pos_x,
                                                         symbol.ast.pos_y)
                            if not symbol.hasParent:
                                symbol.pos_x = symbol.ast.pos_x
                                symbol.pos_y = symbol.ast.pos_y
                            else:
                                symbol.position += relpos
                            symbol.update_connections()
                            # Update_position is called here because it
                            # is not possible to be sure that the
                            # positioning stored in the file will be
                            # rendered correctly on the host platform.
                            # Font rendering may cause slight differences
                            # between Linux and Windows for example.
                            symbol.update_position()
                        else:
                            # No CIF coordinates: fix COMMENT position
                            if isinstance(symbol, genericSymbols.Comment):
                                symbol.pos_x = \
                                  symbol.parent.boundingRect().width() + 15
                                symbol.pos_y = 0
                            if not symbol.hasParent:
                                sc_br = dest_scene.itemsBoundingRect()
                                sy_br = symbol.mapRectToScene(
                                            symbol.boundingRect() |
                                            symbol.childrenBoundingRect())
                                symbol.pos_x += (sc_br.width() - sy_br.x())
                    except AttributeError as err:
                        # no AST, ignore (e.g. Connections, Cornergrabbers)
                        pass
                        #LOG.debug("[render everything] " + str(err))
                    else:
                        # Recursively fix pos of sub branches and followers
                        for branch in (elm for elm in symbol.childSymbols()
                                   if isinstance(elm,
                                         genericSymbols.HorizontalSymbol)):
                            fix_pos_from_ast(branch)
                        fix_pos_from_ast(symbol.next_aligned_symbol())
                        fix_pos_from_ast(symbol.comment)
                for each in dest_scene.floating_symb:
                    fix_pos_from_ast(each)
            except TypeError:
                LOG.error(traceback.format_exc())

            # Render nested scenes, recursively:
            for each in (item for item in dest_scene.visible_symb
                         if item.nested_scene):
                #LOG.debug('Recursive scene: ' + str(each))
                if isinstance(each.nested_scene, ogAST.CompositeState) \
                        and (not each.nested_scene.statename
                             or each.nested_scene in already_created):
                    # Ignore nested state scenes that already exist
                    #LOG.debug('Subscene "{}" ignored'.format(str(each)))
                    continue
                subscene = self.create_subscene(each.context_name, dest_scene)

                already_created.append(each.nested_scene)
                subscene.name = str(each)
                #LOG.debug('Created scene: {}'.format(subscene.name))
                recursive_render(each.nested_scene.content, subscene)
                # uncomment for profiling:
                #LOG.debug(f'{subscene.name} : ' + str(timeit.timeit(partial(recursive_render, each.nested_scene.content, subscene), number=1)))
                each.nested_scene = subscene

            # Make sure all composite states are initially up to date
            # (Needed for the symbol shape to have dashed lines)
            for each in dest_scene.states:
                if str(each).lower() in dest_scene.composite_states.keys():
                    each.nested_scene = dest_scene.composite_states[str(each).lower()]

            # Readonly user flag
            if dest_scene.context == 'process' and dest_scene.readonly:
                for each in dest_scene.editable_texts:
                    each.setTextInteractionFlags(Qt.NoTextInteraction)

        recursive_render(ast, self)


    def refresh(self):
        ''' Scene refresh - make sure it happens only once per cycle '''
        #LOG.debug('scene refresh requested by '
        #          + str(traceback.extract_stack(limit=2)[-2][1:3]))
        if not self.refresh_requested:
            self.refresh_requested = True
            QTimer.singleShot(0, self.scene_refresh)

    def scene_refresh(self):
        ''' Refresh the symbols and connections in the scene '''
        self.refresh_requested = False
        #LOG.debug('scene refresh done')
#       for symbol in self.visible_symb:
#           symbol.updateConnectionPointPosition()
#           symbol.updateConnectionPoints()
        for symbol in self.editable_texts:
            # EditableText refreshing - design explanation:
            # The first one is tricky: at symbol initialization,
            # the bounding rect of the text is computed from the raw
            # text value, without any formatting. However, it can
            # happen that text (especially when a model is loaded)
            # contains highlighted data (bold), which has the effect
            # of making the width of the text in fact wider than
            # the bounding rect. The set_text_alignment function,
            # that is applying the alignment of the text within its
            # bounding rect, can work only if the text width is fixed.
            # It has to set it according to the bounding rect, which,
            # therefore can be too small, and this has the effect of
            # pushing the exceeding character to the next line.
            # The only way to avoid this is to call setTextWidth
            # with the value -1 before the alignment is computed.
            # This has the effect of re-computing the bounding rect
            # and fixing the width issue.
            symbol.setTextWidth(-1)
            #symbol.set_textbox_position()
            symbol.try_resize()
            symbol.set_text_alignment()
            # connect the signal that is emitted when text edit changes word
            symbol.word_under_cursor.connect(self.word_under_cursor.emit)
        #for symbol in self.visible_symb:
        # Already called by try_resize for all editable texts
        #    symbol.update_connections()


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


    def translate_to_origin(self):
        '''
            Translate all items to coordinate system starting at (0,0),
            in order to avoid negative coordinates
        '''
        try:
            min_x = min(item.scenePos().x() for item in self.visible_symb)
            min_y = min(item.scenePos().y() for item in self.visible_symb)
        except ValueError:
            # No item in the scene
            return 0, 0
        delta_x = -min_x if min_x < 0 else 0
        delta_y = -min_y if min_y < 0 else 0
        for item in self.floating_symb:
            item.pos_x += delta_x
            item.pos_y += delta_y
        return delta_x, delta_y


    def set_selection(self, toolbar):
        ''' When the selection has changed, update menu, etc '''
        toolbar.update_menu(self)
        for item in self.selected_symbols:
            item.grabber.display()


    def syntax_errors(self, symb):
        ''' Parse a symbol and return a list of syntax errors '''
        return symb.check_syntax('\n'.join(Pr.generate(symb, recursive=False)))


    def check_syntax(self, symbol) -> bool:
        ''' Check syntax of a symbol and display a pop-up in case of errors '''
        # return True if syntax errors were found

        errors = self.syntax_errors(symbol)

        if not errors:
            symbol.syntax_error = False
            return False

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
            msg_box = QMessageBox(view)
            msg_box.setFont(QFont('UbuntuMono', 10))
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle('OpenGEODE - Syntax Error')
            msg_box.setInformativeText('\n'.join(errs))
            msg_box.setText("Syntax error!")
            msg_box.setStandardButtons(QMessageBox.Discard)
            msg_box.setDefaultButton(QMessageBox.Discard)
            msg_box.exec()
        # There were syntax errors: force user to fix them
        # by returning True to the caller (TextInteraction), which
        # will keep focus
        symbol.syntax_error = True
        return True
        #symbol.edit_text()


    def global_syntax_check(self, ignore=set()):
        ''' Parse each visible symbol in the current scene and its children
            and check syntax using the parser
            Use a mutable parameter to avoid recursion on already visited
            scenes
        '''
        res = True
        reset = not ignore
        ignore.add(self)
        for each in self.visible_symb:
            errors = self.syntax_errors(each)
            if errors:
                res = False
            for err in errors:
                split = err.split()
                if split[0] == 'line' and len(split) > 1:
                    line_col = split[1].split(':')
                    if len(line_col) == 2:
                        # get line and col. line must be decremented because
                        # line 1 is the CIF comment which is not visible
                        line_nb, col = line_col
                        line_nb = int(line_nb) - 1
                        split[1] = f'{line_nb}:{col}'
                pos = each.scenePos()
                split.append (f'in "{str(each)}"')
                fmt = [[' '.join(split), [pos.x(), pos.y()], self.path]]
                log_errors(self.messages_window, fmt, [], clearfirst=False)
                for view in self.views():
                    view.find_symbols_and_update_errors()

        for each in self.all_nested_scenes:
            if each not in ignore:
                if not each.global_syntax_check():
                    res = False
        if reset:
            ignore.clear()
        return res


    def update_completion_list(self, symbol):
        ''' When text has changed on a symbol, update the data dictionary '''
        pr_text = '\n'.join(Pr.generate(symbol,
                                        recursive=False,
                                        nextstate=False, cpy=True))
        symbol.update_completion_list(pr_text=pr_text)
        self.context_change.emit()


    def highlight(self, item):
        ''' Highlight a symbol '''
        if item in self.highlighted or not isinstance(item, Symbol):
            return
        bound = item.boundingRect()
        center = bound.center().x()
        gradient = QLinearGradient(center, 0, center, bound.height())
        gradient.setColorAt(0, Qt.cyan)
        gradient.setColorAt(1, Qt.white)
        self.highlighted[item] = item.brush()
        item.setBrush(QBrush(gradient))

    def clear_highlight(self, item=None, reset=True):
        ''' Remove the highlighting of one item or all items on the scene '''
        if item in self.highlighted:
            self.setBrush(self.highlighted.pop(item))
        if reset:
            for item, brush in self.highlighted.items():
                item.setBrush(brush)
            self.highlighted = {}


    def find_text(self, pattern):
        ''' Return all symbols with matching text '''
        for item in (symbol for symbol in self.items()
                     if isinstance(symbol, EditableText)
                     and symbol.isVisible()):
            try:
                res = re.search(pattern, str(item), flags=re.IGNORECASE)
            except re.error:
                # invalid pattern
                raise StopIteration
            if res:
                yield item


    def search(self, pattern, replace_with=None, cmd=None):
        ''' Search and replace function ; get next search result with key n
        cmd is a user string from the vi bar that by default for a replace
        is "s" (substitute string) but that can be a different command,
        e.g. "state" to limit the substitution to State components'''
        self.clearSelection()
        self.clear_highlight()
        self.clear_focus()
        if pattern.endswith('\\'):
            # Avoid buggy pattern ending with a single backslash
            pattern += '\\'
        self.search_item = self.find_text(pattern)
        self.search_pattern = pattern
        if replace_with:
            with undoCommands.UndoMacro(self.undo_stack, 'Search and Replace'):
                for item in self.search_item:
                    if(cmd and cmd != "s" and
                        item.parentItem().__class__.__name__.lower()
                                                               != cmd.lower()):
                        # filter symbols based on the user command
                        continue
                    new_string = re.sub(pattern,
                                        replace_with,
                                        str(item),
                                        flags=re.IGNORECASE)
                    undo_cmd = undoCommands.ReplaceText(
                                     item, str(item), new_string)
                    self.undo_stack.push(undo_cmd)
                    item.try_resize()
                    item.parentItem().select()
                    self.update_completion_list(item.parent)
            self.refresh()
        else:
            try:
                item = next(self.search_item)
                item = item.parentItem()
                item.select()
                self.highlight(item)
                item.ensureVisible()
            except StopIteration:
                LOG.info('Pattern not found')


    def delete_selected_symbols(self):
        '''
            Remove selected symbols from the scene, with proper re-connections
        '''
        if self.context == 'process' and self.readonly:
            # with readonly flag, forbid item deletion
            return
        self.undo_stack.beginMacro('Delete items')
        for item in self.selected_symbols:
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
            Clipboard.copy(self.selected_symbols)
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
        if self.context == 'process' and self.readonly:
            # with readonly flag, forbid item deletion
            return
        parent = list(self.selected_symbols)
        if len(parent) > 1:
            self.messages_window.addItem(
                    'Cannot paste when several items are selected')
        else:
            parent_item, = parent or [None]
            try:
                new_items = Clipboard.paste(parent_item, self)
            except TypeError as error_msg:
                LOG.error(str(error_msg))
                try:
                    self.messages_window.addItem(str(error_msg))
                except AttributeError:
                    pass
            else:
                self.undo_stack.beginMacro('Paste')
                for item in new_items:
                    # Allow pasting inputs when input is selected
                    # Same for decision answers and connections
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
        self.selectionChanged.emit()


    def sdl_to_statechart(self, basic=True, view=None, ast=None):
        ''' Create a graphviz representation of the SDL model 
            Optionally take a QGraphicsView to use as parent for modals '''
        if ast is None:
            pr_raw = Pr.parse_scene(self)
            pr_data = str('\n'.join(pr_raw))
            ast, _, err = ogParser.parse_pr(string=pr_data)
            self.semantic_errors = True if err else False
        if len(ast.processes) == 1:
            process_ast, = ast.processes
        elif len(ast.process_types) == 1:
            process_ast, = ast.process_types
        else:
            LOG.debug('No statechart to render (no process or process type)')
            return None
        try:
            process_ast.input_signals = \
                    sdlSymbols.CONTEXT.processes[0].input_signals
        except IndexError:
            try:
                process_ast.input_signals = \
                    view.context_history[0].processes[0].input_signals
            except (AttributeError, IndexError):
                # No process context, eg. when called from cmd line
                # in that case ast was provided in the parameters
                LOG.debug("Statechart rendering: no CONTEXT.processes[0]")

        # Flatten nested states (no, because neato does not support it,
        # dot supports only vertically-aligned states, and fdp does not
        # support curved edges and is buggy with pygraphviz anyway)
        # Helper.flatten(process_ast)
        return Statechart.create_dot_graph(process_ast, basic,
                                           scene=self, view=view)


    def export_branch_to_picture(self, symbol, filename, doc_format):
        ''' Save a symbol and its followers to a file '''
        temp_scene = SDL_Scene(context=self.context)
        temp_scene.messages_window = self.messages_window
        self.clearSelection()
        self.clear_highlight()
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
            for item in self.floating_symb:
                name = '{}-{}'.format(filename, str(index))
                LOG.info('Saving {ext} file: {name}.{ext}'
                         .format(ext=doc_format, name=name))
                self.export_branch_to_picture(item, name, doc_format)
                index += 1

        if filename.split('.')[-1] != doc_format:
            filename += '.' + doc_format

        self.clearSelection()
        self.clear_highlight()
        self.clear_focus()
        # Copy in a different scene to get the smallest rectangle
        # (except statecharts, they are already optimal)
        if self.context != "statechart":
            other_scene = SDL_Scene(context=self.context)
            other_scene.messages_window = self.messages_window
            other_scene.setBackgroundBrush(QBrush())
            for each in self.floating_symb:
                each.select()
                try:
                    self.copy_selected_symbols()
                except AttributeError as err:
                    LOG.debug(str(traceback.format_exc()))
                    LOG.error(str(err))
                other_scene.paste_symbols()
                other_scene.scene_refresh()
                each.select(False)
            rect = other_scene.sceneRect()
        else:
            # remove the background
            self.setBackgroundBrush(QBrush())
            self.scene_refresh()
            rect = self.sceneRect()

        # enlarge the rect to fit extra pixels due to antialiasing
        rect.adjust(-5, -5, 5, 5)
        if doc_format == 'png':
            device = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            device.fill(Qt.transparent)
        elif doc_format == 'svg':
            device = QtSvg.QSvgGenerator()
            device.setFileName(filename)
            device.setTitle('OpenGEODE SDL Diagram')
            device.setSize(rect.size().toSize())
        elif doc_format == 'pdf':
            device = QPrinter()
            device.setOutputFormat(QPrinter.PdfFormat)
            device.setPaperSize(
                    rect.size().toSize(), QPrinter.Point)
            device.setFullPage(True)
            device.setOutputFileName(filename)
        else:
            LOG.error('Output format not supported: ' + doc_format)
        painter = QPainter(device)
        if self.context == 'statechart':
            self.render(painter, source=rect)
        else:
            other_scene.scene_refresh()
            other_scene.render(painter, source=rect)
        try:
            device.save(filename)
        except AttributeError:
            # Due to inconsistencies in Qt API - only QImage has the save
            pass
        if painter.isActive():
            painter.end()


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
                    QGraphicsItem.ItemIsSelectable)
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


    def create_subscene(self, context, parent=None):
        ''' Create a new SDL scene, e.g. for nested symbols '''
        subscene = SDL_Scene(context=context, readonly=self.readonly)
        subscene.messages_window = self.messages_window
        subscene.parent_scene = parent
        subscene.context_change.connect(self.context_change.emit)
        subscene.word_under_cursor.connect(self.word_under_cursor.emit)
        return subscene


    def place_symbol(self, item_type, parent, pos=None, rect=None):
        ''' Draw a symbol on the scene '''
        item = item_type()
        if rect is not None:
            # Optionally size the new item
            item.set_shape(rect.width(), rect.height())
        # Add the item to the scene
        if item not in self.items():
            self.addItem(item)
        # Create Undo command (makes the call to the insert_symbol function):
        undo_cmd = undoCommands.InsertSymbol(item=item, parent=parent, pos=pos)
        self.undo_stack.push(undo_cmd)
        # If no item is selected (e.g. new STATE), add it to the scene
        if not parent:
            G_SYMBOLS.add(item)

        if item_type == Decision:
            # When creating a new decision, add two default answers
            self.place_symbol(item_type=DecisionAnswer, parent=item)
            self.place_symbol(item_type=DecisionAnswer, parent=item)
        elif item_type in (Procedure, State, Process):
            # Create a sub-scene for clickable symbols
            item.nested_scene = \
                    self.create_subscene(item_type.__name__.lower(), self)

        self.clearSelection()
        self.clear_highlight()
        self.clear_focus()
        item.select()
        item.cam(item.pos(), item.pos())
        # When item is placed, immediately set focus to input text
        item.edit_text()

        for view in self.views():
            view.view_refresh()
            view.ensureVisible(item)
        return item



    def add_symbol(self, item_type):
        ''' Add a symbol, or postpone until a parent symbol is selected  '''
        try:
            # If an item is selected or if its text has focus,
            # use it as parent item for the newly inserted item
            selection, = (list(self.selected_symbols) or
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
            if item_type == Connection:
                self.mode = 'wait_connection_source'
            else:
                self.mode = 'wait_placement'
            self.set_cursor(item_type)
            return None

    def border_point(self, symb, point):
        ''' Find the closest point on the border of a symbol '''
        rect = symb.sceneBoundingRect()
        center = rect.center()
        h_dist = min(point.y() - rect.y(),
                     rect.y() + rect.height() - point.y())
        v_dist = min(point.x() - rect.x(),
                     rect.x() + rect.width() - point.x())
        res = QPointF()
        res.setX(symb.pos_x
                if point.x() <= center.x()
                else symb.pos_x + symb.boundingRect().width())
        res.setY(symb.pos_y
                if point.y() <= center.y()
                else symb.pos_y + symb.boundingRect().height())
        if h_dist < v_dist:
            res.setX(point.x())
        else:
            res.setY(point.y())
        return res

    # pylint: disable=C0103
    def mousePressEvent(self, event):
        '''
            Handle mouse click on the scene:
            1) If a symbol was selected in the menu, place it in the scene
            2) Otherwise store the coordinates, in which case if the user does
               a paste action with floating items, they will be placed there.
            3) If there is no object at click coordinates, enter the
               selection mode. When mouse is released, check the selection
               rectangle. If no object is selected, open a pop-up menu to
               insert a new symbol, based on the scene context
        '''
        self.reset_cursor()
        # First propagate event to symbols for specific treatment
        super().mousePressEvent(event)
        # Store mouse coordinates as possible paste position
        self.click_coordinates = event.scenePos()
        # Enter state machine
        if self.mode == 'idle' and event.button() == Qt.LeftButton:
            # Idle mode: click triggers selection square
            nearby_connection = self.symbol_near(event.scenePos(),
                                                 selectable_only=False)
            connection_selected = False
            if isinstance(nearby_connection, Connection):
                # Click near a connection - forward the event to it
                # (some connections like statechart Edges can react)
                nearby_connection.mousePressEvent(event)
                connection_selected = True
            symb = self.symbol_near(event.scenePos(), dist=1)
            if not symb:
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
            elif symb.user_can_connect and symb.in_start_zone(event.pos().toPoint()):
                # TODO check if symbol can have more than
                # one connection if there is already one, if start
                # and end can be on the same symbol, etc.
                # DISABLE CONNECTIONS FOR NOW
                pass
#               self.mode = 'wait_next_connection_point'
#               click_point = event.scenePos()
#               point = self.border_point(symb, click_point)
#               self.edge_points = [point]
#               self.temp_lines.append(self.addLine(point.x(),
#                                                   point.y(),
#                                                   click_point.x(),
#                                                   click_point.y()))
#               self.connection_start = symb

        elif self.mode == 'wait_placement':
            try:
                parent = self.can_insert(event.scenePos(),
                                         self.button_selected)
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
        if(event.buttons() == Qt.NoButton and
            self.mode != 'wait_next_connection_point') or self.mode == 'idle':
            return super().mouseMoveEvent(event)
        elif self.mode == 'select_items':
            rect = QRectF(self.orig_pos, event.scenePos())
            self.select_rect.setRect(rect.normalized())
        elif self.mode == 'wait_next_connection_point':
            # Update the line
            line = self.temp_lines[-1].line()
            self.temp_lines[-1].setLine(line.x1(),
                                        line.y1(),
                                        event.scenePos().x(),
                                        event.scenePos().y())

    def quick_menu(self, pos, rect):
        ''' Add actions on the fly to the context-dependent menu that is
        displayed when the user draws a box on the screen '''
        menu       = QMenu('Select item to add')
        singletons = (i.__class__ for i in self.visible_symb if i.is_singleton)
        candidates = filter(lambda x: not x.needs_parent
                                      and not x in singletons,
                            ACTIONS.get(self.context, []))

        def add_symbol(sort, rect):
            size = rect if sort.default_size == "any" else None
            symb = self.place_symbol(sort, parent=None, pos=rect.topLeft(),
                                     rect=size)

        def setup_action(sort):
            name   = sort.__name__
            icon   = QIcon(':icons/{}.png'.format(name.lower()))
            action = menu.addAction(icon, name)
            action.triggered.connect(partial(add_symbol,
                                             sort,
                                             rect=rect))
        if list(map(setup_action, candidates)):
            menu.exec(pos)

    def cancel(self):
        ''' Return to idle mode, reset current actions '''
        try:
            self.select_rect.hide()
        except AttributeError:
            # there may be none
            pass
        for each in self.temp_lines:
            each.setVisible(False)
        self.mode = 'idle'

    # pylint: disable=C0103
    def mouseReleaseEvent(self, event):
        if self.mode == 'select_items':
            found = False
            rect = self.select_rect.rect()
            if self.context != 'statechart':
                # Don't let user unhighlight the current state in statecharts
                self.clear_highlight()
            for item in self.items(rect, mode=Qt.ContainsItemBoundingRect):
                try:
                    if not isinstance(item, Connection):
                        item.select()
                    self.highlight(item)
                except AttributeError:
                    pass
                else:
                    found = True
            if not found and rect.width() > 20 and rect.height() > 20:
                # No items to select, so propose a context dependent menu
                self.quick_menu(event.screenPos(), rect)
            #self.removeItem(self.select_rect)
            # stop with removeItem, it provokes segfault
            self.cancel()
        elif self.mode == 'wait_next_connection_point':
            point = event.scenePos()
            previous = self.edge_points[-1]
            if abs(point.x() - previous.x()) < 15:
                point.setX(previous.x())
            if abs(point.y() - previous.y()) < 15:
                point.setY(previous.y())
            symb = self.symbol_near(point, dist=1)
            if previous != point:
                # Draw a temporary line to the scene
                current_line = self.temp_lines[-1]
                line = current_line.line()
                current_line.setLine(line.x1(), line.y1(),
                                          point.x(), point.y())
                self.edge_points.append(point)
                self.temp_lines.append(self.addLine(point.x(),
                                                    point.y(),
                                                    point.x(),
                                                    point.y()))
            # Decide if the connection is valid, create it accordingly
            valid = (symb and symb.__class__.__name__
                     in self.connection_start._conn_sources and
                     self.connection_start.__class__.__name__
                     in symb._conn_targets)# and
                     #len(self.edge_points) > 2)
                     # (The above was commented because it prevented
                     # direct lines between two blocks)
            # "valid" could also check if it's allowed to connect
            # a symbol to itself.
            if symb and valid:
                nb_segments = len(self.edge_points) - 1
                for each in self.temp_lines[-nb_segments:]:
                    # check lines that collide with the source or dest TODO
                    pass
                # Clicked on a symbol: create the actual connector
                # Use a Channel type by default, but this could be something
                # else in a different context
                connector = Channel(parent=self.connection_start, child=symb)
                # Set start and end points first, so that the distance can
                # be computed when storing the middle points's relative
                # positions
                connector.start_point = self.edge_points[0]
                connector.end_point = self.border_point(symb, point)
                connector.middle_points = self.edge_points[1:-1]
                self.cancel()

        super().mouseReleaseEvent(event)


    # pylint: disable=C0103
    def keyPressEvent(self, event):
        ''' Handle keyboard: Delete, Undo/Redo '''
        super().keyPressEvent(event)
        if event.matches(QKeySequence.Delete) and self.selectedItems():
            self.delete_selected_symbols()
            self.clearSelection()
            self.clear_highlight()
            self.clear_focus()
        elif event.key() == Qt.Key_Escape:
            self.cancel()
        elif event.matches(QKeySequence.Undo):
            if not isinstance(self.focusItem(), EditableText):
                LOG.debug('UNDO ' + self.undo_stack.undoText())
                self.undo_stack.undo()
                self.clearSelection()
                self.clear_highlight()
                self.refresh()
                # Emit a selection change to make sure the toolbar is updated
                # (e.g. when Undoing a Place START symbol)
                self.selectionChanged.emit()
                self.clear_focus()
        elif event.matches(QKeySequence.Redo):
            if not isinstance(self.focusItem(), EditableText):
                LOG.debug('REDO ' + self.undo_stack.redoText())
                self.undo_stack.redo()
                self.clearSelection()
                self.clear_highlight()
                self.refresh()
                self.clear_focus()
                # Emit a selection change to make sure the toolbar is updated
                self.selectionChanged.emit()
        elif event.matches(QKeySequence.Copy):
            if not isinstance(self.focusItem(), EditableText):
                try:
                    self.copy_selected_symbols()
                except TypeError:
                    LOG.error('Cannot copy')
        elif event.matches(QKeySequence.Cut):
            self.cut_selected_symbols()
        elif event.matches(QKeySequence.Paste):
            if not isinstance(self.focusItem(), EditableText):
                self.paste_symbols()
                for view in self.views():
                    # refresh scrollbars
                    view.refresh()
                self.refresh()
                self.clear_focus()
        elif event.key() == Qt.Key_N:
            # n to select the next item in a search (vim mode)
            if self.focusItem():
                # Only active when no item has keyboard focus
                return
            try:
                self.clearSelection()
                self.clear_highlight()
                item = next(self.search_item)
                item = item.parentItem()
                item.select()
                self.highlight(item)
                item.ensureVisible()
            except StopIteration:
                LOG.info('No more matches')
                self.search(self.search_pattern)
            except AttributeError as err:
                LOG.info('No search pattern. Use "/pattern"')
        elif (event.key() == Qt.Key_J and
                event.modifiers() == Qt.ControlModifier):
            # Debug mode
            for selection in self.selected_symbols:
                LOG.info(str(selection))
                LOG.info('Position: ' + str(selection.pos()))
                LOG.info('ScenePos: ' + str(selection.scenePos()))
                LOG.info('BoundingRect: ' + str(selection.boundingRect()))
                #LOG.info('ChildrenList: ' + str(selection.childItems()))
                LOG.info('ChildrenBoundingRect: ' +
                        str(selection.childrenBoundingRect()))
                pprint.pprint(selection.__dict__, None, 2, 1)
            code.interact('type your command:', local=locals())


class SDL_View(QGraphicsView):
    ''' Main graphic view used to display the SDL scene and handle zoom '''
    # signal to ask the main application that a new scene is needed
    need_new_scene = Signal()
    update_asn1_dock = Signal(ogAST.AST)
    # When changing scene the data dictionary has to be updated
    update_datadict = Signal()

    def __init__(self, scene):
        ''' Create the SDL view holding the scene '''
        super().__init__(scene)
        self.wrapping_window = None
        # self.messages_window = None
        self.messages_window = QListWidget()  # default
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
        self.scene_stack = []
        # Set of PR files that are not saved back (e.g. system structure)
        self.readonly_pr = None
        # Context history referencing the AST entry corresponding to the scene
        # Used when navigating between scene with up/down button to update
        # the CONTEXT parameter in sdlSymbols - used for autocompletion
        self.context_history = []
        # Special scene for the Lander module
        self.lander_scene = SDL_Scene(context='lander')
        # Do not initialize the lander now - only if needed
        self.lander = None
        # handle view refresh - once per cycle only
        self.refresh_requested = False
        # Flag indicating that something changed on the model since last time
        # user clicked on the Check Model button
        self.something_changed = True

    top_scene = lambda self: (self.scene_stack[0][0] if self.scene_stack
                              else self.scene())

    is_model_clean = lambda self: not any(not sc.undo_stack.isClean() for sc in
                 chain([self.top_scene()], self.top_scene().all_nested_scenes))

    def change_cleanliness(self, idx):
        ''' When something changed on the scene, notify the view
        via the "something_changed" variable, used to monitor if
        something changed since the last model check. This function is called
        via a signal sent by the undo stack of the scene (indexChanged)'''
        self.something_changed = True

    def set_toolbar(self):
        ''' Define the toolbar depending on the context '''
        self.toolbar.set_actions(
                bar_items=ACTIONS.get(self.scene().context, []))

        # Connect toolbar actions
        self.scene().selectionChanged.connect(partial(
                                    self.scene().set_selection, self.toolbar))
        for item in self.toolbar.actions.keys():
            self.toolbar.actions[item].triggered.connect(
                                                   self.scene().actions[item])
        self.toolbar.update_menu(self.scene())

    # pylint: disable=C0103
    def keyPressEvent(self, event):
        ''' Handle keyboard: Zoom, open/save diagram, etc. '''
        if event.matches(QKeySequence.ZoomOut):
            self.scale(0.8, 0.8)
            # Make sure the scene is resized when zooming in/out
            self.update_phantom_rect()
        elif event.matches(QKeySequence.ZoomIn) or \
           (event.key() == Qt.Key_Plus
            and event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier):
            self.scale(1.2, 1.2)
            # Make sure the scene is resized when zooming in/out
            self.update_phantom_rect()
        elif event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            # Reset zoom with Ctrl-Q
            self.resetTransform()
        elif event.matches(QKeySequence.Save):
            self.save_diagram()
        elif event.key() == Qt.Key_F3 or (event.key() == Qt.Key_G and
                event.modifiers() == Qt.ControlModifier):
            # F3 or Ctrl-G to generate Ada code
            self.generate_ada()
        elif event.key() == Qt.Key_F7:
            self.check_model()
        elif event.key() == Qt.Key_F5:
            self.refresh()
        elif event.matches(QKeySequence.Open):
            self.open_diagram()
        elif event.matches(QKeySequence.New):
            self.new_diagram()
        elif (event.key() == Qt.Key_F12 and
                event.modifiers() == Qt.ControlModifier and
                self.scene() != self.lander_scene):
            self.lander_scene.setSceneRect(0, 0, self.width(), self.height())
            if not self.lander:
                self.lander = Lander.Lander(self.lander_scene)
            horpos = self.horizontalScrollBar().value()
            verpos = self.verticalScrollBar().value()
            self.scene_stack.append((self.scene(), horpos, verpos))
            self.scene().clear_focus()
            self.setScene(self.lander_scene)
            self.up_button.setEnabled(True)
            self.set_toolbar()
            self.lander.play()
        super().keyPressEvent(event)

    def refresh(self):
        ''' View refresh - make sure it happens only once per cycle '''
        #LOG.debug('view refresh requested by '
        #          + str(traceback.extract_stack(limit=2)[-2][0:3]))
        if not self.refresh_requested:
            self.refresh_requested = True
            QTimer.singleShot(0, self.view_refresh)

    def view_refresh(self):
        ''' Refresh the complete view '''
        #LOG.debug('view refresh done')
        self.refresh_requested = False
        self.scene().refresh()
        self.setSceneRect(self.scene().sceneRect())
        self.viewport().update()

    def update_phantom_rect(self):
        scene_rect = self.scene().itemsBoundingRect()
        view_size = self.size()
        scene_rect.setWidth(max(scene_rect.width(), view_size.width()))
        scene_rect.setHeight(max(scene_rect.height(), view_size.height()))
        if self.phantom_rect and self.phantom_rect in self.scene().items():
            self.phantom_rect.setRect(scene_rect)
        else:
            self.phantom_rect = self.scene().addRect(scene_rect,
                    pen=QPen(QColor(0, 0, 0, 0)))
        # Hide the rectangle so that it does not collide with the symbols
        self.phantom_rect.hide()
        self.refresh()

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
        LOG.debug('[QGraphicsView] ResizeEvent')
        self.update_phantom_rect()
        super().resizeEvent(event)

    def about_og(self):
        ''' Display the About dialog '''
        QMessageBox.about(self, 'About OpenGEODE',
                'OpenGEODE SDL editor for TASTE\n\n'
                'Version {}\n\n'
                'Copyright (c) 2012-2019 Maxime Perrotin / European Space Agency\n\n'
                'Contact: Maxime.Perrotin@esa.int\n\n'.format(__version__))

    # pylint: disable=C0103
    def wheelEvent(self, wheelEvent):
        '''
            Catch the mouse Wheel event
        '''
        if wheelEvent.modifiers() == Qt.ControlModifier:
            # Google-Earth zoom mode (Zoom with center on the mouse position)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            if wheelEvent.angleDelta().y() < 0:
                self.scale(0.9, 0.9)
            else:
                self.scale(1.1, 1.1)
            self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
            # Make sure the scene is resized when zooming in/out
            self.update_phantom_rect()
        else:
            return super().wheelEvent(wheelEvent)

    # pylint: disable=C0103
    def mousePressEvent(self, evt):
        '''
            Catch mouse press event to move (when middle button is clicked)
            or to select multiple items
        '''
        # First propagate the click (then scene will receive it first):
        super().mousePressEvent(evt)
        try:
            self.toolbar.update_menu(self.scene())
        except AttributeError:
            # If scene has no menu connected (eg. ASN.1 dock..)
            pass
        self.mouse_pos = evt.pos()
        if evt.button() == Qt.MiddleButton:
            self.mode = 'moveScreen'

    def go_up(self):
        '''
            When Up button is clicked, go up one nested scene level
        '''
        LOG.debug('GO_UP')
        self.scene().clear_focus()
        # Signal to the world that the current scene is left:
        self.scene().scene_left.emit()
        scene, horpos, verpos = self.scene_stack.pop()
        self.setScene(scene)
        self.wrapping_window.setWindowTitle(self.scene().name)
        self.set_toolbar()
        if not self.scene_stack:
            self.up_button.setEnabled(False)
        self.setSceneRect(self.scene().sceneRect())
        self.viewport().update()
        self.horizontalScrollBar().setSliderPosition(horpos)
        self.verticalScrollBar().setSliderPosition(verpos)
        sdlSymbols.CONTEXT = self.context_history.pop()
        self.update_datadict.emit()
        self.scene().undo_stack.cleanChanged.connect(
                lambda x: self.wrapping_window.setWindowModified(not x))
        self.scene().undo_stack.indexChanged.connect(lambda idx :
                    self.change_cleanliness(idx))

    def go_down(self, scene, name=''):
        ''' Enter a nested diagram (procedure, composite state) '''
        # Save context history
        self.context_history.append(sdlSymbols.CONTEXT)
        try:
            subtype, subname = name.split()
        except ValueError as err:
            LOG.debug("[go_down] name split fail (PROCESS TYPE?)" + str(err))
            LOG.info("Can't refine content of a type instance")
            return
        # Get AST of the element that is entered
        if subtype == 'procedure':
            for each in sdlSymbols.CONTEXT.procedures:
                if subname.lower() == each.inputString.lower():
                    sdlSymbols.CONTEXT = each
                    break
            else:
                # Not existing yet - creating the AST context
                new_context = ogAST.Procedure()
                new_context.inputString = subname.lower()
                sdlSymbols.CONTEXT.procedures.append(new_context)
                sdlSymbols.CONTEXT = new_context
        elif subtype == 'state':
            for each in sdlSymbols.CONTEXT.composite_states:
                if subname.lower() == each.statename.lower():
                    sdlSymbols.CONTEXT = each
                    break
            else:
                # Not existing yet - creating the AST context
                new_context = ogAST.CompositeState()
                new_context.statename = subname.lower()
                sdlSymbols.CONTEXT.composite_states.append(new_context)
                sdlSymbols.CONTEXT = new_context
        elif subtype == 'process':
            for each in sdlSymbols.CONTEXT.processes:
                if subname.lower() == each.processName.lower():
                    sdlSymbols.CONTEXT = each
                    break
            else:
                # Not existing yet - creating the AST context
                new_context = ogAST.Process()
                new_context.processName = subname.lower()
                sdlSymbols.CONTEXT.processes.append(new_context)
                sdlSymbols.CONTEXT = new_context
        else:
            LOG.error("Please report BUG: miss support for " + subtype)

        horpos = self.horizontalScrollBar().value()
        verpos = self.verticalScrollBar().value()
        self.scene().name = self.wrapping_window.windowTitle()
        self.scene_stack.append((self.scene(), horpos, verpos))
        self.scene().clear_focus()
        self.setScene(scene)
        self.scene().name = name + '[*]'
        self.wrapping_window.setWindowTitle(self.scene().name)
        self.up_button.setEnabled(True)
        self.set_toolbar()
        self.view_refresh()
        self.scene().scene_left.emit()
        self.update_datadict.emit()
        self.scene().undo_stack.cleanChanged.connect(
                lambda x: self.wrapping_window.setWindowModified(not x))
        self.scene().undo_stack.indexChanged.connect(lambda idx :
                    self.change_cleanliness(idx))

    # pylint: disable=C0103
    def mouseDoubleClickEvent(self, evt):
        ''' Catch a double click - possibly change the scene '''
        super().mouseDoubleClickEvent(evt)
        if evt.button() == Qt.LeftButton:
            item = self.scene().symbol_near(self.mapToScene(evt.pos()))
            try:
                if item.allow_nesting:
                    item.double_click()
                    ctx = str(item.context_name)
                    if not isinstance(item.nested_scene, SDL_Scene):
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle('Create nested symbol')
                        msg_box.setText('Do you want to create a new sub-{} ?'
                                        '\n\n'
                                        'If you do, you can come back to the '
                                        'current diagram using the up arrow '
                                        'in the menu bar on the top of the '
                                        'screen'
                                        .format(item.context_name))
                        msg_box.setStandardButtons(QMessageBox.Yes |
                                                   QMessageBox.Cancel)
                        msg_box.setDefaultButton(QMessageBox.Yes)
                        ret = msg_box.exec()
                        if ret == QMessageBox.Yes:
                            item.nested_scene = \
                                self.scene().create_subscene(ctx, self.scene())
                        else:
                            item.edit_text(self.mapToScene(evt.pos()))
                            return
                    self.go_down(item.nested_scene,
                                 name=u"{} {}".format(ctx, str(item)))
                else:
                    # Otherwise, double-click edits the item text
                    item.edit_text(self.mapToScene(evt.pos()))
            except AttributeError as err:
                LOG.debug('Ignoring double click:' + str(err))

    # pylint: disable=C0103
    def mouseMoveEvent(self, evt):
        ''' Handle the screen move when user clicks '''
        if evt.buttons() == Qt.NoButton:
            return super().mouseMoveEvent(evt)
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
            return super().mouseMoveEvent(evt)

    # pylint: disable=C0103
    # this is a performance killer, ignore (use F5 to refresh)
#   def mouseReleaseEvent(self, evt):
#       self.mode = ''
#       # Adjust scrollbars if diagram got bigger due to a move
#       if self.scene().context != 'statechart':
#           # Make sure scene size remains OK when adding/moving symbols
#           # Avoid doing it when editing texts - it would prevent text
#           # selection or cursor move
#           if not isinstance(self.scene().focusItem(), EditableText):
#               LOG.debug('mouseRelease refresh')
#               self.refresh()
#       super().mouseReleaseEvent(evt)

    def save_as(self):
        ''' Save As function '''
        self.save_diagram(save_as=True)

    def save_diagram(self, save_as=False, autosave=False):
        ''' Save the diagram to a .pr file '''

        if (not self.filename or save_as) and not autosave:
            save_as = True
            self.filename = QFileDialog.getSaveFileName(
                    self, "Save model", ".", "SDL Model (*.pr)")[0]
        if self.filename and self.filename.split('.')[-1] != 'pr':
            self.filename += ".pr"
        filename = ((self.filename or '_opengeode')
                    + '.autosave') if autosave else self.filename

        prj_name = ''.join(
                filename.split(os.path.extsep)[0:-1]).split(os.path.sep)[-1]

        # Need to get the list of .pr (incl e.g. system_structure.pr)
        # for the gpr file
        if len(sdlSymbols.AST.pr_files) > 0:
            first = sdlSymbols.AST.pr_files.pop()
            source_dir = os.path.dirname(first) or '.'
            first_pr = first
        else:
            source_dir = os.path.dirname(filename) or "."
            first_pr = filename

        # other pr files: use relative path to "code" because gprbuild
        # moves to this folder when calling opengeode
        other_pr = ", ".join('"' + os.path.relpath(pr_file, 'code') + '"'
                             for pr_file in sdlSymbols.AST.pr_files)


        # If the current scene is a nested one, save the top parent
        scene = self.top_scene()

        if not scene:
            LOG.info('No scene - nothing to save')
            return False

        if not autosave:
            self.messages_window.clear()
            # Check the model if anything changed (mostly to spot syntax errors
            # as they could jeopardize subsequent model parsing)
            # if not autosave: # and self.something_changed:
            if self.check_model() == "Syntax Errors":
                LOG.error('Syntax errors must be fixed NOW '
                          'or you may not be able to reload the model')
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle('OpenGEODE - Syntax Error')
                msg_box.setText("Syntax errors were found. It is not advised to "
                                "save the model now, as you may not be able to "
                                "open it again. Are you sure you want to save?")
                msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
                res = msg_box.exec()
                if res == QMessageBox.Cancel:
                    return False

        if not filename and not autosave:
            return False

        # Generate the process context in ASN.1
        if scene.ast is not None and len(scene.ast.processes) == 1:
            process, = scene.ast.processes
            process.name = process.processName
            # If this is a process type, use the type for the datamodel
            process = process.instance_of_ref or process
            Helper.code_generation_preprocessing(process)
            Helper.generate_asn1_datamodel(process)

        pr_file = QFile(filename)
        pr_path = QFileInfo(pr_file).path()
        pr_file.open(QIODevice.WriteOnly | QIODevice.Text)

        if not autosave and save_as:
            scene.name = 'block {}[*]'.format(''.join(filename
                    .split(os.path.extsep)[0:-1]).split(os.path.sep)[-1])
            if self.scene() == scene:
                self.wrapping_window.setWindowTitle('{}'
                                                    .format(scene.name))

        # Translate all scenes to avoid negative coordinates
        delta_x, delta_y = scene.translate_to_origin()
        for each in chain([scene], scene.all_nested_scenes):
            dx, dy = each.translate_to_origin()
            if each == self.scene():
                delta_x, delta_y = dx, dy

        pr_raw = Pr.parse_scene(scene, full_model=True
                                       if not self.readonly_pr else False)

        # Read the processes name for the Makefile
        for each in scene.processes:
            if not isinstance(each, ProcessType):
                process_name = str(each.text)
                break

        # Move items back to original place to avoid scrollbar jumps
        for item in self.scene().floating_symb:
            item.pos_x -= delta_x
            item.pos_y -= delta_y

        # Gather list of ASN.1 files (+possibly custom types definitions)
        try:
            firstAsn1File = os.path.basename(ogParser.DV.asn1Files[0])
            source_dir = os.path.relpath\
                    (os.path.dirname(ogParser.DV.asn1Files[0]) or ".")
            otherAsn1Files = [os.path.relpath(path, "code")
                    for path in ogParser.DV.asn1Files[1:]]
        except (AttributeError, IndexError):
            source_dir = "."
            firstAsn1File, otherAsn1Files = "", []

        otherAsn1Files.append(f'code/{prj_name}_datamodel.asn')
        otherAsn = " ".join(otherAsn1Files)

        #  Template for the Makefile
        template_makefile = f'''all:
\tmkdir -p code
\tcd code && opengeode --toAda {first_pr} {other_pr}
\tasn1scc -fp AUTO -typePrefix asn1Scc -o code -equal -Ada {firstAsn1File} {otherAsn}
\tcd code && gnat make {prj_name}
clean:
\trm -rf code'''
        pr_data = str('\n'.join(pr_raw))
        try:
            pr_file.write(pr_data.encode('utf-8'))
            pr_file.close()
            if not autosave:
                # and generate a Makefile.project to build everything
                with open(pr_path + '/Makefile.{}'.format(prj_name), 'w') as f:
                    f.write(template_makefile)
                self.scene().clear_focus()
                for each in chain([scene], scene.all_nested_scenes):
                    each.undo_stack.setClean()
            else:
                LOG.debug('Auto-saving backup file completed:' + filename)
            return True
        except AttributeError:
            LOG.error('Impossible to save the file')
            return False

    def save_png(self):
        ''' Save the current view as a PNG image '''
        filename = QFileDialog.getSaveFileName(
                self, "Save picture", ".", "Image (*.png)")[0]
        self.scene().export_img(filename, doc_format='png')

    def load_file(self, files):
        ''' Parse a PR file and render it on the scene '''
        #cwd = os.getcwd()
        dir_pool = set(os.path.dirname(each) for each in files)
        if len(dir_pool) != 1:
            LOG.warning('Files are spread in several directories - '
                        'ASN.1 files may not be found')
        else:
            files = [os.path.abspath(each) for each in files]
            os.chdir(dir_pool.pop() or '.')
        try:
            ast, warnings, errors = ogParser.parse_pr(files=files)
        except IOError:
            LOG.error('Aborting: could not open or parse input file')
            sdlSymbols.CONTEXT = ogAST.Block()
            return
        if not ast.processes:
            LOG.error("No PROCESS was parsed in the input file(s)")
            process = ogAST.Process()
            process.processName = "Syntax_Error"
        elif len(ast.processes) == 1:
            process,         = ast.processes
            if not process.instance_of_name:
                self.filename    = process.filename
            elif process.instance_of_ref is not None:
                self.filename    = process.instance_of_ref.filename
            else:
                LOG.error("Unrecoverable parsing errors were detected")
                self.messages_window.addItem("Could not parse model")
                return
            self.readonly_pr = ast.pr_files - {self.filename}
        else:
            # More than one process
            LOG.error("More than one process is not supported")
            return
        try:
            syst, = ast.systems
            block, = syst.blocks
            if block.processes[0].referenced:
                LOG.debug('[Load file] Process is referenced')
                block.processes = [process]
        except ValueError:
            # No System/Block hierarchy, creating single block
            block = ogAST.Block()
            block.processes = [process]
        LOG.debug('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        log_errors(self.messages_window, errors, warnings)
        try:
            self.scene().render_everything(block)
        except AttributeError as err:
            LOG.debug("[Rendering] " + str(err))
        self.find_symbols_and_update_errors()
        self.toolbar.update_menu(self.scene())
        self.scene().name = 'block {}[*]'.format(process.processName)
        self.wrapping_window.setWindowTitle(self.scene().name)
        self.refresh()
        self.centerOn(self.sceneRect().topLeft())
        self.scene().undo_stack.clear()
        # Emit a signal for the application to update the ASN.1 scene
        self.update_asn1_dock.emit(ast)
        # Set AST to be used as data dictionary and updated on the fly
        sdlSymbols.AST = ast
        sdlSymbols.CONTEXT = block
        self.update_datadict.emit()

    def open_diagram(self):
        ''' Load one or several .pr file and display the state machine '''
        if not self.new_diagram():
            return
        filenames, _ = QFileDialog.getOpenFileNames(self,
                "Open model(s)", ".", "SDL model (*.pr)")
        if not filenames:
            return
        else:
            self.load_file(filenames)
            self.up_button.setEnabled(False)

    def propose_to_save(self):
        ''' Display a dialog to let the user save his diagram '''
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('OpenGEODE')
        msg_box.setText("The model has been modified.")
        msg_box.setInformativeText("Do you want to save your changes?")
        msg_box.setStandardButtons(QMessageBox.Save |
                QMessageBox.Discard |
                QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Save)
        ret = msg_box.exec()
        if ret == QMessageBox.Save:
            if not self.save_diagram():
                return False
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def new_diagram(self):
        ''' If model state is clean, reset current diagram '''
        if not self.is_model_clean() and not self.propose_to_save():
            return False
        self.need_new_scene.emit()
        self.scene_stack = []
        self.scene().undo_stack.clear()
        G_SYMBOLS.clear()
        self.scene().process_name = ''
        self.filename = None
        self.readonly_pr = None
        self.wrapping_window.setWindowTitle('block[*]')
        self.set_toolbar()
        return True


    def check_model(self):
        ''' Parse the model and check for warnings and errors '''
        # If the current scene is a nested one, go first to the top parent
        scene = self.top_scene()

        # Keep track of this check - to avoid repeating if user wants to
        # save the model. This flag is set back to True if anything is
        # modified in any scene
        self.something_changed = False

        self.messages_window.clear()
        self.messages_window.addItem("Checking syntax")
        if not scene.global_syntax_check():
            self.messages_window.addItem("Aborted. Fix syntax errors first")
            return "Syntax Errors"
        self.messages_window.addItem("No syntax errors")
        self.messages_window.addItem("Checking semantics")

        if scene.context not in ('process', 'state', 'procedure', 'block'):
            # check can only be done on SDL diagrams
            return "Non-SDL"
        # Set use_symbol_id to True so that we save the id (pointer) of the
        # already-rendered symbols. In errors they will be stored as x-coord
        pr_raw = Pr.parse_scene(scene, full_model=True
                                       if not self.readonly_pr else False,
                                       use_symbol_id=True)
        pr_data = str('\n'.join(pr_raw))
        try:
            if pr_data:
                LOG.info("Calling the PR Parser")
                ast, warnings, errors = ogParser.parse_pr(
                        files=self.readonly_pr,
                        string=pr_data)
                LOG.info("Calling the PR Parser: DONE")
                scene.semantic_errors = True if errors else False
                log_errors(self.messages_window, errors, warnings,
                           clearfirst=False)
                LOG.info("Updating errors")
                self.find_symbols_and_update_errors(use_id=True)
                LOG.info("Updating errors: DONE")
                self.update_asn1_dock.emit(ast)
                LOG.info("Semantic Check: COMPLETE")
                # for convenience, attach the ast to the top-level scene
                scene.ast = ast
                return "Done"
            else:
                return "Incomplete check"
        except Exception as err:
            LOG.error("Oops, something went wrong with the semantic checks")
            self.messages_window.addItem("Opengeode bug, PLEASE REPORT: "
                    + str(err))
            LOG.debug(str(traceback.format_exc()))
        return "Syntax Errors"

    def find_symbols_and_update_errors(self, use_id=False):
        ''' Update the list of errors with the actual symbol location
        error list entries contain Qt Data including path and graphical
        coordinates. Based on this, retrieve the actual symbol. Once
        found, it can be read by show_item (i.e. when user clicks on the
        line in the list) to highlight the correct symbol even if it has
        moved.
        This function is called after each call of log_errors()
        if use_id=True it means that the model check was done while the
        symbols have already been rendered. In the case the x coordinate
        is set with the id of the existing symbol. This allows to associate
        it properly with the error without having to rely on x/y coordinates
        to locate the symbol (which takes a big amount of time on large models)
        '''
        messages : QListWidget = self.messages_window
        current_scene = self.scene().path
        # We will remove from the list of errors all those that point
        # to a symbol coordinates, and we will replace them with the
        # errors stored directly in the symbols. This is much faster
        # than looking everywhere to find the symbols by following the path.
        toBeRemoved = []
        for idx in range(messages.count()):
            line : QListWidgetItem = messages.item(idx)
            coord = line.data(Qt.UserRole)
            path = line.data(Qt.UserRole + 1)
            if not coord or coord == ['' , '']:
                # All lines do not contain errors - discard them
                # the second test could be true in case there is no CIF data
                pass
            else:
                # error contains coordinates -> remove it unless it is an id
                if not use_id:
                    toBeRemoved.append(line)
                elif int(coord[0]) != 0:
                    symbol_id = int(coord[0])
                    err = line.text()
                    kind = "ERROR" if err.startswith("[ERROR]") else "WARNING"
                    #LOG.info(f"id : {symbol_id} {line.text()}")
                    # Retrieve the symbol from its id, put it in G_ERRORS
                    # and update its ast.path value and errors/warnings fields
                    # Cast the symbol id to retrieve the (existing) symbol
                    symbol = ctypes.cast(symbol_id, ctypes.py_object).value
                    symbol.ast.path = path
                    if kind == "ERROR":
                        symbol.ast.errors.append(err[6:])
                    else:
                        symbol.ast.warnings.append(err[8:])
                    G_ERRORS.append(symbol)
                    line.setData(Qt.UserRole + 2, len(G_ERRORS) - 1)
                # Find the scene containing the symbol
#               scene = self.scene()
#               if not self.go_to_scene_path(path):
#                   continue
#               pos = QPoint(*coord)
#               symbol = self.scene().symbol_near(pos=pos, dist=1)
#               if symbol is not None:
#                   G_ERRORS.append(symbol)
#                   line.setData(Qt.UserRole + 2, len(G_ERRORS) - 1)
#               else:
#                   print("No symbol at coord", coord, "in scene", path)
#       _ = self.go_to_scene_path(current_scene)
        for each in toBeRemoved:
            row = messages.row(each)
            messages.takeItem(row)
        # Iterate over the items that contain errors and warnings
        if not use_id:
            for idx, item in enumerate(G_ERRORS):
                if not hasattr(item.ast, "errors"):
                    continue
                for err in item.ast.errors:
                    line = QListWidgetItem (f'[ERROR] {err}')
                    line.setData(Qt.UserRole + 1, item.ast.path)
                    line.setData(Qt.UserRole + 2, idx)
                    # Put errors at the beginning of the list
                    messages.insertItem(0, line)
                # Clean up the list of errors
                item.ast.errors = []
                for warn in item.ast.warnings:
                    line = QListWidgetItem (f'[WARNING] {warn}')
                    line.setData(Qt.UserRole + 2, idx)
                    line.setData(Qt.UserRole + 1, item.ast.path)
                    # Put warnings after the errors
                    messages.addItem(line)
                # Clean up the list of warnings
                item.ast.warnings = []


    def go_to_scene_path(self, path) -> bool:
        ''' Reach a specific path (scene) by going up/down. This makes sure
        that the Up button is properly set when the scene is reached '''
        while self.up_button.isEnabled():
            self.go_up()

        for each in path:
            try:
                kind, name = each.split()
            except ValueError as err:
                LOG.debug(f'In go_to_scene_path: {str(each)}')
                return False
            name = str(name).lower()
            if kind.lower() == 'process':
                for process in self.scene().processes:
                    if str(process).lower() == name:
                        self.go_down(process.nested_scene,
                                     name='process {}'.format(name))
                        break
                else:
                    LOG.error(f'Process {name} not found')
                    return False
            elif kind.lower() == 'state':
                for state in self.scene().states:
                    if str(state).lower() == name:
                        self.go_down(state.nested_scene,
                                     name=f'state {name}')
                        break
                else:
                    LOG.error(f'Composite state {name} not found')
                    return False
            elif kind.lower() == 'procedure':
                for proc in self.scene().procedures:
                    if str(proc).lower() == name:
                        self.go_down(proc.nested_scene,
                                     name=f'procedure {name}')
                        break
                else:
                    LOG.error(f'Procedure {name} not found')
                    return False
        return True

    def show_item(self, item):
        '''
           Select an item and make sure it is visible - change scene if needed
           Used when user clicks on a warning or error to locate the symbol
        '''
        coord = item.data(Qt.UserRole)
        path = item.data(Qt.UserRole + 1)
        symb_idx = item.data(Qt.UserRole + 2)
        if symb_idx is not None:
            symbol = G_ERRORS[symb_idx]
            self.scene().clearSelection()
            self.scene().clear_highlight()
            self.scene().clear_focus()
            if not self.go_to_scene_path(path):
                return
            symbol.select()
            self.scene().highlight(symbol)
            self.ensureVisible(symbol)
        else:
            LOG.debug('No coordinates or symbol found')
            return

    def generate_ada(self):
        ''' Generate Ada code '''
        # If the current scene is a nested one, move to the top parent
        scene = self.top_scene()
        pr_raw = Pr.parse_scene(scene, full_model=True
                                       if not self.readonly_pr else False)
        pr_data = str('\n'.join(pr_raw))
        if pr_data:
            ast, warnings, errors = ogParser.parse_pr(files=self.readonly_pr,
                                                      string=pr_data)
            scene.semantic_errors = True if errors else False
            try:
                process, = ast.processes
            except ValueError:
                process = None
            log_errors(self.messages_window, errors, warnings)
            self.find_symbols_and_update_errors()
            if len(errors) > 0:
                self.messages_window.addItem(
                        'Aborting: too many errors to generate code')
            else:
                self.messages_window.addItem('Generating Ada code')
                try:
                    AdaGenerator.generate(process)
                    self.messages_window.addItem('Done')
                except (TypeError, ValueError, NameError) as err:
                    err=str(err).encode('utf8')
                    self.messages_window.addItem(
                            'Code generation failed:' + str(err))
                    LOG.debug(str(traceback.format_exc()))


class OG_MainWindow(QMainWindow):
    ''' Main GUI window '''
    def __init__(self, parent=None):
        ''' Create the main window '''
        super().__init__(parent)
        self.view = None
        self.statechart_view = None
        self.statechart_scene = None
        self.vi_bar = Vi_bar()
        # Docking areas
        self.asn1_browser = None  # type: QTextBrowser
        self.help_browser = None  # type: QTextBrowser
        #self.datatypes_scene = None
        self.asn1_area = None
        # MDI area (need to keep them to avoid segfault due to pyside bugs)
        self.mdi_area = None
        self.sub_mdi = None
        self.statechart_mdi = None
        self.current_window = None
        self.datadict = None

    def new_scene(self, readonly=False):
        ''' Create a new, clean SDL scene. This function is necessary because
        it is not possible to use QGraphicsScene.clear(), because of Pyside
        bugs with deletion of items on application exit '''
        scene = SDL_Scene(context='block', readonly=readonly)
        if self.view:
            scene.messages_window = self.view.messages_window
            self.view.setScene(scene)
            self.view.refresh()
            scene.undo_stack.cleanChanged.connect(lambda x :
                lambda x: self.view.wrapping_window.setWindowModified(not x))
            scene.undo_stack.indexChanged.connect(lambda idx :
                    self.view.change_cleanliness(idx))
            scene.context_change.connect(self.update_datadict_window)
            scene.word_under_cursor.connect(self.select_in_datadict_window)

    def start(self, options, splash, app):
        ''' Initializes all objects to start the application '''

        file_name = options.files
        # widget wrapping the view. We have to maximize it
        process_widget = self.findChild(QWidget, 'process')
        process_widget.showMaximized()

        # Find SDL_View widget
        self.view = self.findChild(SDL_View, 'graphicsView')
        self.view.wrapping_window = process_widget
        self.view.wrapping_window.setWindowTitle('block unnamed[*]')

        # Create a default (block) scene for the view
        self.new_scene(options.readonly)

        # Find Menu Actions
        open_action = self.findChild(QAction, 'actionOpen')
        new_action = self.findChild(QAction, 'actionNew')
        save_action = self.findChild(QAction, 'actionSave')
        save_as_action = self.findChild(QAction, 'actionSaveAs')
        quit_action = self.findChild(QAction, 'actionQuit')
        check_action = self.findChild(QAction, 'actionCheck_model')
        about_action = self.findChild(QAction, 'actionAbout')
        ada_action = self.findChild(QAction, 'actionGenerate_Ada_code')
        png_action = self.findChild(QAction, 'actionExport_to_PNG')

        # Connect menu actions
        open_action.triggered.connect(self.view.open_diagram)
        save_action.triggered.connect(self.view.save_diagram)
        save_as_action.triggered.connect(self.view.save_as)
        quit_action.triggered.connect(self.close)
        new_action.triggered.connect(self.view.new_diagram)
        check_action.triggered.connect(self.view.check_model)
        about_action.triggered.connect(self.view.about_og)
        ada_action.triggered.connect(self.view.generate_ada)
        png_action.triggered.connect(self.view.save_png)

        # Connect signal to let the view request a new scene
        self.view.need_new_scene.connect(self.new_scene)

        # Add a toolbar widget (not in .ui file due to pyside bugs)
        toolbar = Sdl_toolbar(self)

        # Associate the toolbar to the scene
        self.view.toolbar = toolbar

        # Set initial toolbar to the PROCESS editor
        self.view.set_toolbar()

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Add a toolbar with New/Open/Save/Check buttons
        filebar = File_toolbar(self)
        filebar.open_button.triggered.connect(self.view.open_diagram)
        filebar.new_button.triggered.connect(self.view.new_diagram)
        filebar.check_button.triggered.connect(self.view.check_model)
        filebar.save_button.triggered.connect(self.view.save_diagram)
        self.view.up_button = filebar.up_button
        filebar.up_button.triggered.connect(self.view.go_up)
        self.addToolBar(Qt.TopToolBarArea, filebar)

        # get the messages list window (to display errors and warnings)
        # it is a QListWidget
        msg_dock = self.findChild(QDockWidget, 'msgDock')
        msg_dock.setWindowTitle('Use F7 to check the model or update the '
                                'Data view, and F3 to generate Ada code')
        msg_dock.setStyleSheet('QDockWidget::title {background: lightgrey;}')
        messages = self.findChild(QListWidget, 'messages')
        messages.addItem('Welcome to OpenGEODE.')
        self.view.messages_window = messages
        self.view.scene().messages_window = messages
        messages.itemClicked.connect(self.view.show_item)
        self.mdi_area = self.findChild(QMdiArea, 'mdiArea')
        self.sub_mdi = self.mdi_area.subWindowList()
        self.filter_event = FilterEvent()
        for each in self.sub_mdi:
            each.widget().installEventFilter(self.filter_event)
            if each.widget() != process_widget:
                self.statechart_mdi = each
                self.mdi_area.subWindowActivated.connect(self.upd_statechart)
                break

        self.statechart_view = self.findChild(SDL_View, 'statechart_view')
        self.statechart_scene = SDL_Scene(context='statechart')
        self.statechart_view.setScene(self.statechart_scene)

        # Set up the dock area to display the ASN.1 Data model
        asn1_dock = self.findChild(QDockWidget, 'datatypes_dock')
        dict_dock = self.findChild(QDockWidget, 'datadict_dock')
        help_dock = self.findChild(QDockWidget, 'help_dock')
        self.tabifyDockWidget(asn1_dock, dict_dock)
        self.tabifyDockWidget(asn1_dock, help_dock)
        self.asn1_browser = self.findChild(QTextBrowser, 'asn1_browser')
        self.view.update_asn1_dock.connect(self.set_asn1_view)
        #self.help_browser = self.findChild(OG_HelpBrowser, 'help_browser')
        # Set up the content of the Help tab: use a splitter to have an
        # area with Index/Contents/Search and an area with the actual html
        # content.
        self.help_browser = OG_HelpBrowser()
        splitter = QSplitter (Qt.Horizontal)
        tWidget = QTabWidget()
        tWidget.setMaximumWidth(200)
        helpContent = self.help_browser.engine.contentWidget()
        helpIndex   = self.help_browser.engine.indexWidget()
        tWidget.addTab(helpContent, "Contents")
        tWidget.addTab(helpIndex,   "Index")
        # Search tab:
        helpSearch     = self.help_browser.engine.searchEngine()
        queryWidget    = helpSearch.queryWidget()
        resultWidget   = helpSearch.resultWidget()
        searchSplitter = QSplitter(Qt.Vertical)
        searchSplitter.insertWidget(0, queryWidget)
        searchSplitter.insertWidget(1, resultWidget)
        tWidget.addTab(searchSplitter, "Search")
        def search_help():
            # for some reason the search widget does not search automatically
            helpSearch.search(queryWidget.searchInput())
        queryWidget.search.connect(search_help)

        splitter.insertWidget(0, tWidget)
        splitter.insertWidget(1, self.help_browser)
        help_dock.setWidget(splitter)
        helpContent.linkActivated.connect(self.help_browser.setSource)
        helpIndex.linkActivated.connect(self.help_browser.setSource)
        resultWidget.requestShowLink.connect(self.help_browser.setSource)





        # Set up the data dictionary window
        self.datadict = self.findChild(QTreeWidget, 'datadict')
        self.datadict.setAlternatingRowColors(True)
        self.datadict.setColumnCount(2)
        self.datadict.itemClicked.connect(self.datadict_item_selected)

        QTreeWidgetItem(self.datadict, ["ASN.1 Data types"])
        QTreeWidgetItem(self.datadict, ["ASN.1 Constants"])
        QTreeWidgetItem(self.datadict, ["Input signals"])
        QTreeWidgetItem(self.datadict, ["Output signals"])
        QTreeWidgetItem(self.datadict, ["States"])
        QTreeWidgetItem(self.datadict, ["Labels"])
        QTreeWidgetItem(self.datadict, ["Variables"])
        QTreeWidgetItem(self.datadict, ["Timers"])
        self.view.update_datadict.connect(self.update_datadict_window)

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
            splash.showMessage("Loading model...",
                       alignment=Qt.AlignCenter | Qt.AlignBottom)
            app.processEvents()
            types = []
            self.view.load_file(file_name)
        else:
            # Create a default context - at Block level - for the autocompleter
            sdlSymbols.CONTEXT = ogAST.Block()
            self.update_datadict_window()

        # After file was loaded, try to restore window geometry
        self.restoreApplicationState()



    @Slot(QMdiSubWindow)
    def upd_statechart(self, mdi):
        ''' Signal sent by Qt when the MDI area tab changes
        Here we check if the Statechart tab is selected, and we draw/refresh
        the statechart automatically in that case '''
        if(mdi == self.statechart_mdi and
           mdi != self.current_window and not Statechart.locked()):
            # this signal is executed even when model windows are open
            # so the lock is necessary to prevent recursive execution
            scene = self.view.top_scene()
            try:
                graph = scene.sdl_to_statechart(view=self.view)
                if graph:
                    Statechart.render_statechart(self.statechart_scene,
                                                 graph)
                    self.statechart_view.refresh()
                    self.statechart_view.fitInView(
                            self.statechart_scene.itemsBoundingRect(),
                            Qt.KeepAspectRatioByExpanding)
            except (AttributeError, IOError, TypeError) as err:
                LOG.debug(str(traceback.format_exc()))
                LOG.debug("Statechart error: " + str(err))
        if mdi is not None:
            # When leaving the focus, this signal is received with mdi == None
            # but the window is not changed, so don't update current_window
            self.current_window = mdi


    @Slot(QTreeWidgetItem, int)
    def datadict_item_selected(self, item, column):
        ''' Slot called when user clicks on an item of the data dictionary '''
        parent = item.parent()
        if not parent:
            # user clicked on a root item
            return

        index = self.datadict.indexOfTopLevelItem(parent)
        root = {0: 'asn1 types', 1: 'asn1 constants', 2: 'input signals',
                3: 'output signals', 4: 'states', 5: 'labels', 6: 'variables',
                7: 'timers'}[index]

        anchor = item.data(0, ANCHOR)
        if root == 'asn1 types' and anchor and column == 1:
            self.asn1_browser.scrollToAnchor(anchor)
            # Activate the tab to display the ASN.1 type in html
            self.asn1_browser.parent().parent().raise_()
        elif root in ('states', 'labels') and column == 0:
            name = item.text(column)
            if self.view.scene().search_pattern != name:
                self.view.scene().search(item.text(column))
                self.view.setFocus()
            else:
                # Already selected, show next match
                key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_N,
                                            Qt.NoModifier)
                QApplication.sendEvent(self.view.scene(), key_event)
        elif root == 'states' and column == 1:
            state = item.text(0)
            self.vi_bar.setText(':%state,{},new_name,'.format(state))
            self.vi_bar.cursorWordBackward(False)
            self.vi_bar.cursorWordBackward(True)
            self.vi_bar.show()
            self.vi_bar.setFocus()


    @Slot(ogAST.AST)
    def set_asn1_view(self, ast):
        ''' Display the ASN.1 types in the dedicated scene '''
        # Update the dock widget with ASN.1 files content
        try:
            html_file = open(ast.DV.html, 'r')
        except AttributeError:
            LOG.debug('set_asn1_view: No ASN.1 file specified')
            return
        html_content = html_file.read()
        self.asn1_browser.setHtml(html_content)
        self.asn1_browser.setFont(QFont('UbuntuMono', 12))

        # Update the data dictionary
        item_types = self.datadict.topLevelItem(0)
        item_types.takeChildren() # remove old children
        for name, sort in sorted(ast.dataview.items()):
            new_item = QTreeWidgetItem(item_types,
                                             [name.replace('-', '_'),
                                              'view'])
            new_item.setForeground(1, Qt.blue)
            # Save type anchor for html
            new_item.setData(0, ANCHOR, "ASN1_" + name.replace('-', '_'))
        item_constants = self.datadict.topLevelItem(1)
        item_constants.takeChildren()
        for name, sort in ast.asn1_constants.items():
            sortname = sort.type.ReferencedTypeName \
                    if sort.type.kind.startswith('Reference') \
                    else sort.type.kind[:-4]
            QTreeWidgetItem(item_constants,
                                 [name.replace('-', '_'),
                                 sortname])
        # Expand the types tree to make sure the size of the colum is ok
        item_types.setExpanded(True)
        item_constants.setExpanded(True)
        self.datadict.resizeColumnToContents(0)

    def select_in_datadict_window(self, str):
        ''' This function is called upon reception of a signal emitted by
        text boxes when the current word under the cursor has changed. This
        function then looks in the data dictionary and if the text is found,
        the relevant row is selected. This allows user to easily retrieve
        the type of a variable for instance '''
        (in_sig, out_sig, states, labels,
         dcl, timers) = [self.datadict.topLevelItem(i) for i in range(2, 8)]
        for idx in range(dcl.childCount()):
            child = dcl.child(idx)
            if child.text(0).lower() == str.lower():
                child.treeWidget().setCurrentItem(child)
                child.treeWidget().scrollToItem(child)


    def update_datadict_window(self):
        ''' Update the tree in the data dictionary based on the AST '''
        # currently the ast is a global in sdlSymbols.CONTEXT
        # it should be attached to the current scene instead TODO
        (in_sig, out_sig, states, labels,
         dcl, timers) = [self.datadict.topLevelItem(i) for i in range(2, 8)]
        context = sdlSymbols.CONTEXT
        def change_state(item, state):
            ''' Disable (with state=True) or enable (state=False) one of the
            root items of the data dictionary '''
            item.setDisabled(state)
            item.takeChildren()

        def refresh_signals(root, signals):
            for each in signals:
                sort = each.get('type', '')
                sort = sort.ReferencedTypeName if sort else ''
                QTreeWidgetItem(root, [each['name'], sort])

        add_elem = lambda root, elem: QTreeWidgetItem(root, [elem])

        if self.view.scene().context == 'block':
            for each in (in_sig, out_sig, states, labels, dcl, timers):
                change_state(each, True)
        elif self.view.scene().context == 'process':
            for each in (in_sig, out_sig, states, labels, dcl, timers):
                change_state(each, False)
            refresh_signals(in_sig, context.input_signals)
            refresh_signals(out_sig, context.output_signals)

            for each in sorted(context.mapping.keys()):
                if each != 'START':
                    state = QTreeWidgetItem(states, [each, 'refactor'])
                    state.setForeground(1, Qt.blue)

            for each in sorted(l.inputString for l in context.labels):
                add_elem(labels, each)

            for each in sorted(context.timers):
                add_elem(timers, each)

            for var, (sort, _) in context.variables.items():
                try:
                    sort_name = sort.ReferencedTypeName
                except AttributeError:
                    sort_name = "Undefined"
                    self.view.messages_window.addItem(
                            'Warning: Type of variable "{}" is undefined'
                            .format(var))
                QTreeWidgetItem(dcl, [var, sort_name])

        elif self.view.scene().context == 'procedure':
            for each in (in_sig, states):
                change_state(each, True)
            for each in (dcl, timers, labels, out_sig):
                change_state(each, False)

            for var, (sort, _) in context.variables.items():
                QTreeWidgetItem(dcl, [var, sort.ReferencedTypeName])

            for each in sorted(l.inputString for l in context.labels):
                add_elem(labels, each)

            for each in sorted(context.timers):
                add_elem(timers, each)
            refresh_signals(out_sig, context.output_signals)
        self.datadict.resizeColumnToContents(0)

    def vi_command(self):
        # type: () -> None
        '''
            Process a vi command as entered in the Vi command line
            Supported commands:
            :<w><q><!> (save, quit)
            /<search pattern>
            :%s/<search_patten>/<replace_with>/g
        '''
        command = self.vi_bar.text()
        # Match vi-like search and replace pattern (e.g. :%s,a,b,g)
        # any command is supported, not only substitute
        search = re.compile(r':%(\w+)(.)(.*)\2(.*)\2(.)?')
        try:
            cmd, _, pattern, new, loc = search.match(command).groups()
            LOG.debug('Replacing {this} with {that}'
                          .format(this=pattern, that=new))
            if loc != 'g':
                # apply only to the current scene
                self.view.scene().search(pattern, replace_with=new, cmd=cmd)
            else:
                # apply globally to the whole model
                scene = self.view.top_scene()
                for each in chain([scene], scene.all_nested_scenes):
                    each.search(pattern, replace_with=new, cmd=cmd)
        except AttributeError as err:
            # Developer command allowing to dynamically reload a
            # python module, to avoid heavy roundtrips while debugging
            # (quit tool, fix bugs, reload, test)
            cmd = command.split()
            LOG.debug(cmd)
            if len(cmd) == 2 and cmd[0] == ":reload":
                mod = cmd[1]
                if mod == "ogParser":
                    LOG.debug (f"Reloading {ogParser.__file__}")
                    # save context
                    dv = ogParser.DV
                    tmp = ogParser.TMPVAR
                    reload(ogParser)
                    ogParser.DV = dv
                    ogParser.TMPVAR = tmp
                elif mod == "sdlSymbols":
                    LOG.debug (f"Reloading {sdlSymbols.__file__}")
                    ast = sdlSymbols.AST
                    ctxt = sdlSymbols.CONTEXT
                    reload(sdlSymbols)
                    sdlSymbols.AST = ast
                    sdlSymbols.CONTEXT = ctxt
                elif mod == "genericSymbols":
                    LOG.debug (f"Reloading {genericSymbols.__file__}")
                    reload(genericSymbols)
                else:
                    LOG.error(f"Cannot reload {mod} module")
            elif command.startswith('/') and len(command) > 1:
                LOG.debug('Searching for ' + command[1:])
                self.view.scene().search(command[1:])
                self.view.setFocus()
            else:
                saveclose = re.compile(r':(w)?(q)?(!)?')
                try:
                    save, close_app, force = saveclose.match(command).groups()
                    if save:
                        saved = self.view.save_diagram()
                        if not saved and not force and close_app:
                            return
                    if force and close_app:
                        self.view.scene().undo_stack.clear()
                    if close_app:
                        self.close()
                    return
                except AttributeError:
                    pass

    # pylint: disable=C0103
    def keyPressEvent(self, key_event):
        ''' Handle keyboard: Enable the vi command line '''
        if key_event.key() == Qt.Key_Colon:
            self.vi_bar.show()
            self.vi_bar.setFocus()
            self.vi_bar.setText(':')
        elif key_event.key() == Qt.Key_Slash:
            self.vi_bar.show()
            self.vi_bar.setFocus()
            self.vi_bar.setText('/')
        super().keyPressEvent(key_event)

    # pylint: disable=C0103
    def closeEvent(self, event):
        ''' Close main application after saving application state '''
        if not self.view.is_model_clean() and not self.view.propose_to_save():
            event.ignore()
        else:
            # save windows geometry to a setting file
            if self.view.filename:
                ini_filename = self.view.filename + ".ini"
                settings = QSettings(ini_filename, QSettings.IniFormat)
                settings.setValue('geometry', self.saveGeometry())
                settings.setValue('windowState', self.saveState())

            # Clear the list of top-level symbols to avoid possible exit-crash
            # due to pyside badly handling items that are not part of any scene
            G_SYMBOLS.clear()
            # Also clear undo stack that may keep reference to items
            scene = self.view.top_scene()
            for each in chain([scene], scene.all_nested_scenes):
                each.undo_stack.clear()
            super().closeEvent(event)

    def restoreApplicationState(self):
        ''' Restore windows geometry and state '''
        if self.view.filename:
            ini_filename = self.view.filename + ".ini"
            settings = QSettings(ini_filename, QSettings.IniFormat)
            self.restoreGeometry(settings.value('geometry'))
            self.restoreState(settings.value('windowState'))
        #else:
        #    Commented: maximizing the window is annoying
        #    self.setWindowState(Qt.WindowMaximized)


class FilterEvent(QObject):
    def eventFilter(self, obj, event):
        ''' Used to intercept the close event sent of the Mdi windows '''
        if event.type() == QEvent.Close:
            event.ignore()
            return True
        else:
            return QObject.eventFilter(self, obj, event)


def parse_args():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    parser.add_argument('-g', '--debug', action='store_true', default=False,
            help='Display debug information')
    parser.add_argument('--shared', action='store_true', default=False,
            help='Generate getters/setters to access internal state')
    parser.add_argument('--dll', action='store_true', default=False,
            help='Generate callback hooks when compiling as shared object')
    parser.add_argument('--stg', type=str, metavar='file',
            help='Generate code using a custom String Template file')
    parser.add_argument('--check', action='store_true', dest='check',
            help='Check a .pr file for syntax and semantics')
    parser.add_argument('--toAda', dest='toAda', action='store_true',
            help='Generate Ada code for the .pr file')
    parser.add_argument('--llvm', dest='llvm', action='store_true',
            help='Generate LLVM IR code for the .pr file (experimental)')
    parser.add_argument('--toC', dest='toC', action='store_true',
            help='Generate C code for the .pr file ')
    parser.add_argument("-O", dest="optimization", metavar="level", type=int,
            action="store", choices=[0, 1, 2, 3], default=0,
            help="Set optimization level for the generated LLVM IR code")
    parser.add_argument('--png', dest='png', action='store_true',
            help='Generate a PNG file for the process')
    parser.add_argument('--pdf', dest='pdf', action='store_true',
            help='Generate a PDF file for the process')
    parser.add_argument('--svg', dest='svg', action='store_true',
            help='Generate a SVG file for the process')
    parser.add_argument('--split', dest='split', action='store_true',
            help='Save pictures in multiple files (one per floating item)')
    parser.add_argument('--readonly', dest='readonly', action='store_true',
            help='Set process diagram as read-only')
    parser.add_argument('--taste', dest='taste_target', action='store_true',
            help='Generate code for TASTE targets')
    parser.add_argument('files', metavar='file.pr', type=str, nargs='*',
            help='SDL file(s)')
    return parser.parse_args()


def init_logging(options):
    ''' Initialize logging '''
    terminal_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(terminal_formatter)
    LOG.addHandler(handler_console)

    if options.debug:
        level = logging.DEBUG
        faulthandler.enable()
    else:
        level = logging.INFO

    # Set log level for all libraries
    LOG.setLevel(level)
    for each in MODULES:
        each.LOG.addHandler(handler_console)
        each.LOG.setLevel(level)


def parse(files):
    ''' Parse files '''
    if not files:
        raise IOError('No input .pr files')
    cwd = os.getcwd()
    LOG.info('Checking ' + str(files))
    # move to the directory of the .pr files (needed for ASN.1 parsing)
    path = os.path.dirname(files[0])
    files = [os.path.abspath(each) for each in files]
    os.chdir(path or '.')
    ast, warnings, errors = ogParser.parse_pr(files=files)
    LOG.info('Parsing complete. '
             'Summary, found {} warnings and {} errors'
             .format(len(warnings), len(errors)))
    for warning in warnings:
        LOG.warning(warning[0])
    for error in errors:
        LOG.error(error[0])
    os.chdir (cwd)

    return ast, warnings, errors


def generate(process, options):
    ''' Generate code '''
    ret = 0
    if options.toAda or options.shared or options.dll:
        LOG.info('Generating Ada code')
        try:
            AdaGenerator.generate(process,
                                  simu=options.shared,
                                  taste=options.taste_target)
        except (TypeError, ValueError, NameError) as err:
            ret = 1
            err = str(err).replace(u'\u00fc', '.')
            err = err.encode('utf-8')
            LOG.error(str(err))
            LOG.debug(str(traceback.format_exc()))
            LOG.error('Ada code generation failed')
    if options.toC:
        LOG.info('Generating C code')
        try:
            CGenerator.generate(process, simu=options.shared, options=options)
        except (TypeError, ValueError, NameError) as err:
            ret = 1
            LOG.error(str(err))
            LOG.debug(str(traceback.format_exc()))
            LOG.error('C generation failed')
    if options.llvm:
        LOG.info('Generating LLVM code')
        try:
            LlvmGenerator.generate(process, options=options)
        except (TypeError, ValueError, NameError) as err:
            ret = 1
            LOG.error(str(err))
            LOG.debug(str(traceback.format_exc()))
            LOG.error('LLVM IR generation failed')

    if options.stg:
        LOG.info('Using backend file {}'.format(options.stg))
        StgBackend.generate(process, simu=options.shared, stgfile=options.stg)
    return ret


def export(ast, options):
    ''' Export process (command-line option to save model to png, pdf, svg) '''
    # Qt must be initialized before using SDL_Scene
    _ = init_qt()

    # Initialize the clipboard
    Clipboard.CLIPBOARD = SDL_Scene(context='clipboard')

    export_fmt = []
    if options.png:
        export_fmt.append('png')
    if options.pdf:
        export_fmt.append('pdf')
    if options.svg:
        export_fmt.append('svg')
    if not export_fmt:
        return

    process, = ast.processes
    try:
        syst, = ast.systems
        block, = syst.blocks
        if block.processes[0].referenced:
            LOG.debug('Process is referenced, fixing')
            block.processes = [process]
    except ValueError:
        # No System/Block hierarchy, creating single block
        block = ogAST.Block()
        block.processes = [process]

    scene = SDL_Scene(context='block')
    scene.render_everything(block)
    # Update connections, placements
    scene.scene_refresh()

    scenes = [scene]
    for each in set(scene.all_nested_scenes):
        if any(each.visible_symb):
            scenes.append(each)

    for idx, diagram in enumerate(scenes):
        for doc_fmt in export_fmt:
            name = '{}-{}-{}-{}'.format(str(idx),
                                        process.processName,
                                        diagram.context,
                                        diagram.name or 'main')
            LOG.info('Saving {}.{}'.format(name, doc_fmt))
            diagram.export_img(name, doc_format=doc_fmt, split=options.split)
        if diagram.context == 'block':
            # Also save the statechart view of the current scene
            sc_scene = SDL_Scene(context='statechart')
            try:
                graph = diagram.sdl_to_statechart(ast=ast)
                Statechart.render_statechart(sc_scene, graph)
                for doc_fmt in export_fmt:
                    name = 'sc-' + process.processName
                    LOG.info('Saving {}.{}'.format(name, doc_fmt))
                    sc_scene.export_img(name, doc_format=doc_fmt)
            except (AttributeError, IOError, TypeError) as err:
                LOG.error(traceback.format_exc())
                LOG.debug(str(err))


def cli(options):
    ''' Run CLI App '''
    try:
        ast, warnings, errors = parse(options.files)
    except IOError as err:
        LOG.error('Aborting due to parsing error')
        LOG.error(str(err))
        return 1

    if len(ast.processes) != 1:
        LOG.error(f'Found {len(ast.processes)} process(es) instead of one')
        return 1

    if options.png or options.pdf or options.svg:
        export(ast, options)

    if any((options.toAda, options.llvm, options.shared,
        options.stg, options.dll, options.toC)):
        if not errors:
            errors = generate(ast.processes[0], options)
        else:
            LOG.error('Too many errors, cannot generate code')

    return 0 if not errors else 1


def init_qt():
    ''' Initialize Qt '''
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def gui(options):
    ''' Run GUI App '''
    LOG.debug('Running the GUI')
    LOG.info('Model backup enabled - auto-saving every 2 minutes')

    app = init_qt()
    app.setApplicationName('OpenGEODE')
    app.setWindowIcon(QIcon(':icons/input.png'))

    # Set all encodings to utf-8 in Qt
    # This was removed in Qt5, the consequences are unclear
    #QTextCodec.setCodecForCStrings(QTextCodec.codecForName('UTF-8'))

    # Bypass system-default font, to harmonize size on all platforms
    font_database = QFontDatabase()
    font_database.addApplicationFont(':fonts/Ubuntu-RI.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-R.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-B.ttf')
    font_database.addApplicationFont(':fonts/Ubuntu-BI.ttf')
    font_database.addApplicationFont(':fonts/UbuntuMono-RI.ttf')
    font_database.addApplicationFont(':fonts/UbuntuMono-R.ttf')
    font_database.addApplicationFont(':fonts/UbuntuMono-B.ttf')
    font_database.addApplicationFont(':fonts/UbuntuMono-BI.ttf')
    app.setFont(QFont('Ubuntu', 10))

    # Initialize the clipboard
    Clipboard.CLIPBOARD = SDL_Scene(context='clipboard')
    Clipboard.SYS_CLIPBOARD = app.clipboard()

    # Load the application layout from the .ui file
    loader = QUiLoader()
    loader.registerCustomWidget(OG_MainWindow)
    loader.registerCustomWidget(SDL_View)
    loader.registerCustomWidget(OG_HelpBrowser)
    ui_file = QFile(':/opengeode.ui')
    ui_file.open(QFile.ReadOnly)
    my_widget = loader.load(ui_file)
    ui_file.close()
    # Create a splash screen while model is loading
    pixmap = QPixmap(":/icons/splashscreen.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("Welcome to Opengeode!",
                       alignment=Qt.AlignCenter | Qt.AlignBottom)
    app.processEvents()

    my_widget.start(options, splash, app)

    splash.finish(my_widget)

    return app.exec()


def opengeode():
    ''' Tool entry point '''
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    options = parse_args()

    init_logging(options)

    LOG.debug('Starting OpenGEODE version ' + __version__)
    if any((options.check, options.toAda, options.png, options.pdf,
            options.svg, options.llvm, options.shared, options.stg,
            options.dll, options.toC)):
        return cli(options)
    else:
        return gui(options)


if __name__ == '__main__':
    ''' Run main application '''
    cwd = os.getcwd()
    # Windows only: argv[0] may not contain anything if binary is called
    # from the current directory (no "./" prefix on Windows, even if the
    # current folder is not in the PATH). In that case add it to the PATH
    if os.name == 'nt' or hasattr(sys, 'frozen'):
        os.environ['PATH'] += os.pathsep + os.path.abspath(
                                           os.path.dirname(sys.argv[0]) or cwd)
    ret = opengeode()
    os.chdir(cwd)
    sys.exit(ret)
