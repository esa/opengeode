#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Generic library containing the definition of top-level symbols
    that can be used to create diagrams.

    The Symbol class contains common behaviour shared by inherited
    symobols - in particular the VerticalSymbol is a class of symbols
    that can only be vertically aligned ; Horizontal symbols, on the
    other hand, can be move in both directions.

    The "Comment" class of symbols is a floating symbol that is
    connected to a parent symbol on the right.

    This library also contains the defintition of connections
    (the Connection class).

    Symbols can have an editable text area, which behaviour is
    defined in the EditableText class. This class uses the Completer
    and Highlighter class for text auto-completion and syntax
    highlighting.


    Major functionalities offered by the generic Symbol classes are
    the insersion and deletion of items (possibly recursively if there
    are child symbols), the moving and resizing, the collision
    avoidance manoeuvres (when moving a group of symbols on top
    of another group, it has the effect of "pushing" the colliders
    so that symbols never "touch" each others - keeping the diagram
    clean.

    In order to create a specific diagram editor, the user of this
    library shall create his own symbols, that inherit either from
    Horizontal- or VerticalSymbol classes. The geometry of the symbol
    has to be defined in these subclass by defining the polygon
    and other properties (colours, filling, etc.). Some methods can
    be redefined if a particular behaviour is required (e.g. resizing
    differently, holding different connections points, etc).

    For a complete example, look at the "sdlSymbols.py" module, that
    provide symbol definitions that correspond to an SDL editor.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin for the TASTE project

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Symbol', 'VerticalSymbol', 'HorizontalSymbol', 'Comment']
import os
import logging

from PySide.QtCore import Qt, QPoint, QPointF, QRect, QFile, QObject, Property

from PySide.QtGui import(QGraphicsPathItem, QGraphicsPolygonItem, QPainterPath,
                         QGraphicsItem, QPen, QColor, QMenu, QFileDialog,
                         QPainter, QLineEdit, QTextBlockFormat, QPolygonF,
                         QApplication)

from PySide.QtUiTools import QUiLoader

import undoCommands
import ogAST
import ogParser
from Connectors import Connection, VerticalConnection, CommentConnection, \
                       RakeConnection, JoinConnection

from TextInteraction import EditableText

LOG = logging.getLogger(__name__)


# pylint: disable=R0904, R0902
class Symbol(QObject, QGraphicsPathItem, object):
    '''
        Top-level class used to handle all SDL symbols
        Inherits from QObject to allow animations
    '''
    # Symbols of a given type share a text-autocompletion list:
    completion_list = set()
    # Flexible lists of symbol types that can be set as child of this symbol
    _unique_followers = []  # unique : e.g. comment symbol
    _insertable_followers = []  # no limit to insert below current symbol
    _terminal_followers = []  # cannot be inserted between two symbols
    # By default a symbol is resizeable
    resizeable = True
    # By default symbol size may expand when inner text exceeds border
    auto_expand = True
    # By default connections between symbols are lines, not arrows
    arrow_head = None
    arrow_tail = None
    # Default mouse cursor
    default_cursor = Qt.SizeAllCursor
    # Decide if a symbol can be copy-pasted several times
    is_singleton = False
    # default textbox alignment: centered in the symbol
    # can differ on specific symbols (e.g. TextArea or label)
    textbox_alignment = Qt.AlignCenter
    # Common name is the name of the symbol as used in a parser or backend
    common_name = ''
    # Specify if a symbol always needs to be the child of another symbol
    # or if it can live standalone on the scene (yet can have children)
    needs_parent = True
    # nested_scene : a symbol may have content that can be visible on demand
    # (e.g. a subscene that appears when double-clicking on the item)
    _allow_nesting = False
    _nested_scene = None
    # keywords for the syntax highlighter
    blackbold = ()
    redbold = ()
    # Specify if the symbol can be drawn with anti-aliasing
    _antialiasing = True
    # Specify if the symbol has a text area
    has_text_area = True

    def __init__(self, parent=None):
        '''
            Create top level symbol and propagate important properties
            from parent items
        '''
        super(Symbol, self).__init__(parent)
        QGraphicsPathItem.__init__(self, parent)
        self.mode = ''
        self.comment = None
        self.text = None
        # Grabber allowing to resize the item
        self.grabber = Cornergrabber(parent=self)
        self.hyperlink_dialog = None
        self.hlink_field = None
        self.loadHyperlinkDialog()
        # hasParent compensates a Qt (or PySide) bug when calling parentItem()
        # on top-level items
        self.hasParent = False
        self.parent = None
        # Optional parser for the symbol textual representation
        self.parser = None
        # branch entry point allows working with aligned symbols
        self.branch_entrypoint = None
        # Terminal symbol can be used to identify last items of a branch
        self._terminal_symbol = False
        # and default text alignment within a textbox
        self.text_alignment = Qt.AlignLeft
        # Activate cache mode to boost rendering by calling paint less often
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # Apply symbol default mouse cursor
        self.setCursor(self.default_cursor)
        # De-ativate cache mode otherwise paint is not properly updated
        # for the comment symbol (need to refresh on_the_right property)
        self.setCacheMode(QGraphicsItem.NoCache)
        # Initialize variables used when moving/resizing
        self.coord = self.position
        self.height = 0
        self.old_rect = self.boundingRect()
        # List of visible connection points (that can move)
        self.movable_points = []

    def set_valid_pos(self, pos):
        ''' Hook that can be redefined by sub classes to forbid wrong
        placements on the fly, before calling the actual setPos() from Qt '''
        self.setPos(pos)

    # The "position" property cannot be defined as a standard Python
    # property because it is used in a QPropertyAnimation, which only
    # works using Qt properties. However it behaves the same way.
    position = Property(QPointF, lambda self: self.pos(),
                                 lambda self, val: self.set_valid_pos(val))

    pos_x = Property(float, lambda self: self.x(),
                            lambda self, val:
                                    self.set_valid_pos(QPointF(val, self.y())))

    pos_y = Property(float, lambda self: self.y(),
                            lambda self, val:
                                    self.set_valid_pos(QPointF(self.x(), val)))

    def is_composite(self):
        ''' Return True if nested scene has something in it '''
        try:
            return any(self._nested_scene.visible_symb)
        except AttributeError:
            return False

    @property
    def allowed_followers(self):
        '''
            Compute dynamically the list of connectable symbols based on
            the list of current connections and authorized children
        '''
        followers = list(self._insertable_followers)
        for item_type in self._unique_followers:
            # Unique followers: can only be one of this type (e.g. comment)
            if not [child for child in self.childSymbols()
                    if isinstance(child, eval(item_type))]:
                followers.append(item_type)
        if not self.next_aligned_symbol():
            followers.extend(self._terminal_followers)
        return followers

    @property
    def allow_nesting(self):
        ''' Dynamically check if the scene can have a nested subscene
            May be redefined in subclasses and checked on double-click
        '''
        return self._allow_nesting

    @property
    def nested_scene(self):
        ''' Return the nested scene. Can be redefined '''
        return self._nested_scene

    @nested_scene.setter
    def nested_scene(self, value):
        ''' Set the value of the nested scene '''
        self._nested_scene = value

    def closest_connection_point(self, coord):
        '''
           Given a position (QPointF), expected in this symbol's
           coordinates, return the closest connection
           point on the current symbol.
           By default, return the RELATIVE POSITION of a point on the
           bounding rectangle.
        '''
        width = self.boundingRect().width()
        height = self.boundingRect().height()
        top, bottom = self.y(), self.y() + height
        left, right = self.x(), self.x() + width
        x, y = left + coord.x(), top + coord.y()
        if (x > right or x < left) and (y < top or y > bottom):
            # Coord is completely outside the rectangle area
            # in that case, return one of the angles of the bounding rect
            nearest_x = (coord.x() - width if x > right else coord.x())
            nearest_y = (coord.y() if y < top else coord.y() - height)
        elif x >= left and x <= right:
            # x is within the rectangle
            nearest_x = 0
            nearest_y = (coord.y() if abs(y - top) < abs(y - bottom)
                                   else coord.y() - height)
        elif y >= top and y <= bottom:
            # y is within the rectangle (lower priority than x)
            nearest_x = (coord.x() if abs(x - left) < abs(x - right)
                                   else coord.x() - width)
            nearest_y = 0
        return nearest_x, nearest_y

    @property
    def terminal_symbol(self):
        ''' Way to determine if a symbol is terminal (useful for branches) '''
        return self._terminal_symbol

    @terminal_symbol.setter
    def terminal_symbol(self, value):
        ''' Attribute is set per symbol '''
        self._terminal_symbol = value

    def __str__(self):
        ''' Print the text inside the symbol '''
        import traceback
        print traceback.print_stack()
        raise TypeError('Use unicode() not str()')

    def __unicode__(self):
        ''' Return the text inside the symbol '''
        return unicode(self.text) or u'no_name'

    def get_ast(self, pr_text):
        ''' Return the symbol in the AST form, as returned by the parser '''
        ast, _, _, _, terminators = \
                self.parser.parseSingleElement(self.common_name, pr_text)
        return ast, terminators

    def edit_text(self, pos=None):
        '''
            Set the focus on the text area for edition. Position is optional
            Can be called when user double clicks on an item
            Position is in scene coordinates
        '''
        _ = pos
        try:
            # Only one text area is supported for now - ignoring position
            self.text.setFocus()
        except AttributeError:
            return

    def update_completion_list(self, **kwargs):
        '''
            Update the text autocompletion list based on the symbol text
            This function is typically called when user has typed new text
            and it must be redefined per symbol
        '''
        pass

    def check_syntax(self, text):
        ''' Check the syntax of the text inside the symbol (if any) '''
        try:
            _, syntax_errors, _, _, _ = self.parser.parseSingleElement(
                                           self.common_name, text)
        except (AssertionError, AttributeError):
            LOG.error('Checker failed - no parser for this construct?')
        else:
            return syntax_errors

    def paint(self, painter, _, ___):
        ''' Apply anti-aliasing or not (symbol attribute) '''
        painter.setRenderHint(QPainter.Antialiasing, self._antialiasing)
        super(Symbol, self).paint(painter, _, ___)

    def update_position(self):
        ''' VIRTUAL - implemented in subclasses '''
        pass

    def select(self, selected=True):
        ''' When item is selected, effectively select its grabber '''
        self.grabber.setSelected(selected)

    def insert_symbol(self, parent, x, y):
        '''
            Set attributes related to the parent item when inserting the symbol
            in the scene. This method is redefined in subclasses
        '''
        if parent:
            self.hasParent = True
            self.parent = parent
            self.setParentItem(parent)

    def delete_symbol(self):
        '''
            Remove the symbol: pass ownership from parent to caller
            (undo command)
        '''
        entrypoint_parent = None
        if self.branch_entrypoint:
            # If the item is the last in a branch, make clean connections
            bep = self.branch_entrypoint
            entrypoint_parent = bep.parentItem()
            if bep.last_branch_item is self:
                # Last item of a branch, remove or reconnect the link
                # to the connection point
                for child in self.childItems():
                    # Find the connection point below
                    if isinstance(child, JoinConnection):
                        connection_below = child
                        break
                if bep is not self:
                    # Item is not the branch entry point itself
                    bep.last_branch_item = self.parentItem()
                    connection_below.setParentItem(self.parentItem())
                    #self.parentItem().connectionBelow = connection_below
                else:
                    # delete the link to the connection point
                    connection_below.setParentItem(None)
                    self.scene().removeItem(connection_below)
        child_below = self.next_aligned_symbol()
        if(child_below and self.hasParent and
                self.parentItem().next_aligned_symbol() is self):
            # Delete the connection to the child below if
            # it is not a full branch to be deleted
            child_below.connection.setParentItem(None)
            self.scene().removeItem(child_below.connection)
        if self.hasParent:
            if (not child_below or not self.parentItem().next_aligned_symbol()
                    or self.branch_entrypoint is self):
                # If nothing below or item is branch entry point,
                # remove the connection with the parent
                self.connection.setParentItem(None)
                self.scene().removeItem(self.connection)
            else:
                # Otherwise connect the item below with the parent
                child_below.connection = self.connection
                self.connection.child = child_below
                child_below.parent = self.parentItem()
                child_below.setParentItem(child_below.parent)
                # Update position of child - take place of deleted item
                child_below.pos_y = self.pos_y
                child_below.update_position()
            self.parentItem().cam(self.parentItem().position,
                                  self.parentItem().position)
            self.setParentItem(None)
        # Following line causes segfault on exit:
        #scene().removeItem(self)
        try:
            entrypoint_parent.updateConnectionPointPosition()
            entrypoint_parent.updateConnectionPoints()
        except AttributeError:
            pass

    def connect_to_parent(self):
        ''' Add a connection (wire) with the parent item '''
        return Connection(self.parent, self)

    def connection_to_parent(self):
        ''' Return the connection above the symbol '''
        try:
            connection, = [cnx for cnx in self.parent.connections()
                           if cnx.child == self]
            return connection
        except ValueError:
            return None

    def next_aligned_symbol(self):
        ''' Return the next symbol in the flow - implemented in subclasses '''
        return None

    def connections(self):
        ''' Return all child connections of this symbol '''
        return (c for c in self.childItems() if isinstance(c, Connection))

    def loadHyperlinkDialog(self):
        ''' Load dialog from ui file for defining hyperlink '''
        loader = QUiLoader()
        ui_file = QFile(':/hyperlink.ui')  # UI_DIALOG_FILE)
        ui_file.open(QFile.ReadOnly)
        self.hyperlink_dialog = loader.load(ui_file)
        ui_file.close()
        self.hyperlink_dialog.accepted.connect(self.hyperlinkChanged)
        self.hlink_field = self.hyperlink_dialog.findChild(QLineEdit, 'hlink')

    def hyperlinkChanged(self):
        ''' Update hyperlink field '''
        if not self.text:
            return
        hlink = self.hlink_field.text()
        if hlink:
            self.text.setHtml('<a href="{hlink}">{text}</a>'.format
                  (hlink=hlink, text=unicode(self.text).replace('\n', '<br>')))
            self.text.hyperlink = hlink
        else:
            self.text.hyperlink = None
            self.text.setPlainText(unicode(self.text))

    def contextMenuEvent(self, event):
        ''' When user right-clicks: display context menu '''
        png_action = 'Export branch to PNG, SVG or PDF'
        hl_action = 'Hyperlink'
        my_menu = QMenu(png_action)
        if not hasattr(self, '_no_hyperlink'):
            my_menu.addAction(hl_action)
        my_menu.addAction(png_action)
        action = my_menu.exec_(event.screenPos())
        if action:
            if action.text() == png_action:
                # Save a picture of the selected symbol and all its children
                filename = QFileDialog.getSaveFileName(self.window(),
                        'Export picture', '.',
                        'Picture (*.png, *.svg, *.pdf)')[0]
                if not filename:
                    return
                save_fmt = filename.split(os.extsep)[-1]
                if save_fmt not in ('png', 'svg', 'pdf'):
                    return
                self.scene().export_branch_to_picture(self, filename, save_fmt)
            elif action.text() == hl_action:
                if self.text:
                    self.hyperlink_dialog.setParent(
                            self.scene().views()[0], Qt.Dialog)
                    self.hlink_field.setText(self.text.hyperlink)
                    self.hyperlink_dialog.show()

    def childSymbols(self):
        ''' Return the list of child symbols, excluding text/connections '''
        return (item for item in self.childItems() if isinstance(item, Symbol))

    def resize_item(self, rect):
        ''' resize item, e.g. when editing text - move children accordingly '''
        if not self.resizeable:
            return
        delta_x = (self.boundingRect().width() - rect.width()) / 2.0
        delta_y = self.boundingRect().height() - rect.height()
        self.set_shape(rect.width(), rect.height())
        # Align children properly when resizing
        try:
            self.text.set_textbox_position()
        except AttributeError:
            # if called before text is initialized - or if no textbox
            pass
        for child in self.childSymbols():
            child.pos_x -= delta_x
            child.pos_y -= delta_y
        # X-pos must be updated when resizing
        self.pos_x += delta_x
        if self.comment:
            self.comment.pos_x -= delta_x
            self.comment.pos_y += delta_y / 2.0
        self.update_connections()

    def update_connections(self):
        '''
           When symbol moves or is resized, update the shape of all
           its connections - can be redefined in subclasses
        '''
        for cnx in self.connections():
            cnx.reshape()
        try:
            self.connection_to_parent().reshape()
        except AttributeError:
            pass
        try:
            self.branch_entrypoint.parent.update_connections()
        except AttributeError:
            pass

    def set_shape(self, width, height):
        ''' to be implemented per symbol in subclasses '''
        _, ___ = width, height
        self.prepareGeometryChange()
        self.updateConnectionPoints()
        # Update grabber size to fit the new shape size
        self.grabber.display()
        if self.hasParent:
            self.update_position()

    def mouse_click(self, _):
        '''
            Handle resizing and moving of items when grabbing
            the lower right corner
        '''
        # Save current position to be able to revert move
        self.coord = self.position
        rect = self.boundingRect()
        self.height = rect.height()
        if self.grabber.resize_mode != '':
            self.mode = 'Resize'
            self.old_rect = self.boundingRect()
        else:
            self.mode = 'Move'

    def double_click(self):
        ''' Handle double click on symbol - redefined at symbol level '''
        pass

    def mouse_move(self, event):
        ''' Handle resizing of items - moving is handled in subclass '''
        self.updateConnectionPoints()
        # If any, update movable end points of connections
        for point in self.movable_points:
            point.edge.end_connection.update_position()
        if self.mode == 'Resize':
            # Define the resizing based on where item has been grabbed
            if self.grabber.resize_mode.endswith('right'):
                user_width = user_width = event.pos().x()
            elif self.grabber.resize_mode.endswith('left'):
                user_width = self.boundingRect().width() - event.pos().x()
            else:
                user_width = self.boundingRect().width()
            if self.grabber.resize_mode.startswith('bottom'):
                user_height = event.pos().y()
            else:
                user_height = self.boundingRect().height()
            # Minimum size is the size of the text inside the symbol
            try:
                height = max(user_height,
                             self.text.boundingRect().height() + 10)
                width = max(user_width,
                            self.text.boundingRect().width() + 30)
            except AttributeError:
                height = max(user_height, 15)
                width = max(user_width, 30)
            self.resize_item(QRect(0, 0, width, height))

    def mouse_release(self, _):
        ''' Default action when mouse is released: reset mode '''
        if self.mode == 'Resize' and self.old_rect != self.boundingRect():
            with undoCommands.UndoMacro(self.scene().undo_stack, 'Resize'):
                undo_cmd = undoCommands.ResizeSymbol(
                                           self, self.old_rect,
                                           self.boundingRect())
                self.scene().undo_stack.push(undo_cmd)
                self.cam(self.coord, self.position)
                self.updateConnectionPoints()
        elif self.mode == 'Move' and self.coord != self.position:
            with undoCommands.UndoMacro(self.scene().undo_stack, 'Move'):
                undo_cmd = undoCommands.MoveSymbol(
                                            self, self.coord, self.position)
                self.scene().undo_stack.push(undo_cmd)
                self.cam(self.coord, self.position)
        self.mode = ''

    def updateConnectionPoints(self):
        ''' Recursively update connection points (decision branch lengths) '''
        if(self.branch_entrypoint and self.branch_entrypoint.hasParent):
            self.branch_entrypoint.parentItem().updateConnectionPointPosition()
            self.branch_entrypoint.parentItem().updateConnectionPoints()

    def updateConnectionPointPosition(self):
        ''' Implemented in the relevant subclass '''
        pass

    def top_level(self):
        ''' If the item is in a branch, return the highest level in the branch,
            e.g. the starting state. '''
        top_level = self
        while top_level.hasParent:
            # The "or top_level.parent" below is due to a Pyside/Qt bug
            # of the parentItem() function. It can happen that even when
            # the parent has explicitely been set with "setParentItem",
            # a subsequent call to parentItem returns None. Seems to happen
            # if the parent has not been added yet to the scene.
            top_level = top_level.parentItem() or top_level.parent
        return top_level

    # pylint: disable=R0914
    def cam(self, old_pos, new_pos, ignore=None):
        ''' Collision Avoidance Manoeuvre for top level symbols '''
        # Since the cam function is recursive it may be time consuming
        # Call the Qt event prcessing to avoid blocking the application
        # Removed (had bad visual side effects)
        # QApplication.processEvents()
        #print 'CAM', unicode(self)[slice(0, 20)]
        ignore = ignore or []
        if not self.scene():
            # Make sure the item is in a scene. For instance, when loading
            # a model from a file, some items may be connected together
            # and CAM called *before* the top-level item has been inserted.
            return

        top_level = self.top_level()
        if top_level != self:
            # Exectute CAM on top level of this item
            top_level.cam(top_level.position, top_level.position)
            return

        # In case CAM is called due to object move, go to the new position
        delta = new_pos - old_pos

        # Rectangle of current group of item in scene coordinates
        rect = (self.sceneBoundingRect() |
                self.mapRectToScene(self.childrenBoundingRect()))

        # Move the rectangle to the new position, and move the current item
        animation = False
        if self.position != new_pos:
            animation = True
            rect.adjust(delta.x(), delta.y(), delta.x(), delta.y())
            undo_cmd = undoCommands.MoveSymbol(
                    self, old_pos, new_pos, animate=animation)
            self.scene().undo_stack.push(undo_cmd)
            self.position = new_pos

        # Get all items in the rectangle when placed at the new position
        items = self.scene().items(rect)

        # Filters: we keep only items that collide with the group
        # at the new position

        # (a) Filter out items from the current group
        items = [i for i in items
                if (not self.isAncestorOf(i) and i is not self)
                and isinstance(i, Symbol)]

        # (b) Filter out items that are in the rectangle but that do not
        #     actually collide with the current group
        items = [i for i in items if [j for j in i.collidingItems() if
            self.isAncestorOf(j) or j is self]]

        # (c) Filter out the potentially colliding items
        #     if they belong in the cam caller and keep only top-level items
        items = {i.top_level() for i in items if not
                any(c for c in ignore if i.commonAncestorItem(c))}

        # Determine how much we need to move the colliding groups and call
        # their CAM with this delta
        # Save colliders positions in case they are moved by a sub cam call
        col_pos = {i: i.position for i in items}
        for col in items:
            collider_rect = (col.sceneBoundingRect() |
                    col.mapRectToScene(col.childrenBoundingRect()))
            if old_pos.y() + rect.height() <= collider_rect.y():
                # Collision from the top: move down the collider
                delta.setX(col.x())
                delta.setY(rect.y() + rect.height() + 10)
            elif old_pos.y() >= collider_rect.y() + collider_rect.height():
                # Collision from below: move up the collider
                delta.setX(col.x())
                delta.setY(rect.y() - collider_rect.height() - 10)
            elif old_pos.x() <= col.x():
                # Collision from the left: move right
                delta.setX(rect.x() + rect.width() + 10 +
                        col.x() - collider_rect.x())
                delta.setY(col.y())
            else:
                delta.setX(col.x() - collider_rect.x() -
                        collider_rect.width() - 10 + rect.x())
                delta.setY(col.y())
            if col.position == col_pos[col]:
                #print unicode(self), 'collides with', unicode(col)
                col.cam(col.position, delta, ignore=ignore + [self])
                # Put it back at the new position to make sure recursive
                # CAM can happen properly with all object in new positions
                # (End of CAM reset to the old position for animation)
                col.position = delta
        # Place top level colliders in old position so that animation can run
        for col in items:
            col.position = col_pos[col]
        self.update_connections()
        if animation:
            # If animation is planned, it will trigger only when Qt
            # control loop runs again. Going back to original position
            # so that the animation can be done from the starting point
            self.position = old_pos
        #print 'returning from cam'


class Comment(Symbol):
    '''
        Class used to handle right connected comments
    '''
    # Define reserved keywords for the syntax highlighter
    blackbold = ('TODO', 'FIXME', 'XXX')
    redbold = ()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Comment()
        self.ast = ast
        super(Comment, self).__init__(parent)
        self.connection = None
        self.set_shape(ast.width, ast.height)
        self.text = EditableText(parent=self,
                                 text=ast.inputString,
                                 hyperlink=ast.hyperlink)
        if parent:
            local_pos = parent.mapFromScene(ast.pos_x or 0, ast.pos_y or 0)
            self.insert_symbol(parent, local_pos.x(), local_pos.y())
        #self.set_shape(ast.width, ast.height)
        self.common_name = 'end'
        self.parser = ogParser

    def __str__(self):
        return 'Comment'

    @property
    def on_the_right(self):
        ''' Determine if the comment symbol needs to be flipped '''
        return self.x() > self.parent.boundingRect().width() + 5

    def insert_symbol(self, parent, x, y):
        ''' Align the symbol on the right of the parent '''
        if not parent:
            return
        parent.comment = self
        super(Comment, self).insert_symbol(parent, x, y)
        self.pos_x = x if x is not None else parent.boundingRect().width() + 20
        self.pos_y = y if y is not None else (parent.boundingRect().height() -
                                              self.boundingRect().height()) / 2
        self.connection = self.connect_to_parent()
        #parent.cam(parent.position, parent.position)

    def connect_to_parent(self):
        ''' Redefinition of the function to use a comment connector '''
        return CommentConnection(self.parent, self)

    def delete_symbol(self):
        '''
            Specific delete actions for Comment:
            reset comment field in parent
        '''
        self.parentItem().comment = None
        super(Comment, self).delete_symbol()

    def resize_item(self, rect):
        '''
            Redefinition of the Resize function
            (Comment symbol only resizes in one direction)
        '''
        if not self.resizeable or self.grabber.resize_mode.endswith('left'):
            return
        self.set_shape(rect.width(), rect.height())
        self.update_connections()

    def set_shape(self, width, height):
        ''' Set a box - actual shape is computed in the paint function '''
        path = QPainterPath()
        path.addRect(0, 0, width, height)
        self.setPath(path)
        super(Comment, self).set_shape(width, height)

    def paint(self, painter, _, ___):
        ''' Draw the comment symbol '''
        rect = self.boundingRect()
        pen = QPen()
        pen.setStyle(Qt.DashLine)
        pen.setColor(Qt.darkGray)
        painter.setPen(pen)
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        if self.on_the_right:
            painter.drawLines([QPoint(w, y), QPoint(x, y),
                               QPoint(x, y), QPoint(x, h),
                               QPoint(x, h), QPoint(w, h)])
        else:
            painter.drawLines([QPoint(x, y), QPoint(w, y),
                               QPoint(w, y), QPoint(w, h),
                               QPoint(w, h), QPoint(x, h)])

    def mouse_move(self, event):
        ''' Handle item move '''
        super(Comment, self).mouse_move(event)
        if self.mode == 'Move':
            self.pos_y += event.pos().y() - event.lastPos().y()
            self.pos_x += event.pos().x() - event.lastPos().x()
            self.update_connections()

    def mouse_release(self, event):
        '''
            Check if the new position is valid (no collision)
            undo otherwise
        '''
        move_accepted = True
        for item in self.collidingItems():
            if isinstance(item, Symbol):
                move_accepted = False
        if not move_accepted:
            self.position = self.coord
            self.update_connections()
        return super(Comment, self).mouse_release(event)

    def updateConnectionPoints(self):
        '''
            Disable the update of connection points
            (comments do not influence them)
        '''
        pass


class Cornergrabber(QGraphicsPolygonItem, object):
    '''
        Corner grabber is used to resize an item, whatever its shape.
        Such an item is needed because when symbols have a non-rectangular
        shape, the selection area being limited to the item actual borders,
        there is no possibility to grab all items. The cornergrabber is
        a rectangle that covers the full parent bounding rect, allowing
        to resize it from any border/corner.
    '''
    hasParent = False

    def __init__(self, parent):
        ''' Create the grabber '''
        super(Cornergrabber, self).__init__(parent)
        self.setParentItem(parent)
        self.parent = parent
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                QGraphicsItem.ItemIsMovable)
        self.setPos(0, 0)
        self.setPen(QColor(0, 0, 0, 0))
        # Accept hover events (when mouse passes over the item)
        self.setAcceptHoverEvents(True)
        self.show()
        # resize_mode indicates the direction when resizing
        self.resize_mode = ''

    def __repr__(self):
        ''' Pretty string for the print function '''
        return u'Cornergrabber of ' + unicode(self.parentItem())

    def display(self):
        ''' Polygon is a rectangle of the size of the parent item '''
        self.prepareGeometryChange()
        rect = self.parent.boundingRect()
        self.setPos(0, 0)
        self.setPolygon(QPolygonF(rect))
        self.show()

    def mousePressEvent(self, event):
        ''' Handle Qt event '''
        self.parent.mouse_click(event)
        super(Cornergrabber, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        ''' Handle Qt event '''
        self.parent.mouse_move(event)

    def mouseReleaseEvent(self, event):
        ''' Handle Qt event '''
        self.parent.mouse_release(event)

    def hoverMoveEvent(self, event):
        ''' When mouse moves inside the box, set the mouse cursor '''
        pos = event.pos()
        if self.parent.cursor().shape() != self.parent.default_cursor:
            # Parent item may have changed its cursor (e.g. when inserting
            # items). In that case, don't override the cursor for that area
            cursor = self.parent.cursor()
        elif not self.parent.resizeable:
            cursor = self.parent.default_cursor
            self.resize_mode = ''
        # Left side
        elif 0.0 <= pos.x() <= 10.0:
            # Top-left corner: disabled
            #if pos.y() <= 10.0:
            #    cursor = Qt.SizeFDiagCursor
            if pos.y() > self.boundingRect().height() - 10.0:
                cursor = Qt.SizeBDiagCursor
                self.resize_mode = 'bottom_left'
            else:
                cursor = Qt.SizeHorCursor
                self.resize_mode = 'left'
        # Middle of item
        elif 5.0 < pos.x() < self.boundingRect().width() - 10.0 and (
                     pos.y() > self.boundingRect().height() - 10.0):
            cursor = Qt.SizeVerCursor
            self.resize_mode = 'bottom'
        # Right side
        elif(self.boundingRect().width() - 5.0 <= pos.x()
                                <= self.boundingRect().width()):
            # Top-right corner: disabled
            #if pos.y() <= 10.0:
            #    cursor = Qt.SizeBDiagCursor
            if pos.y() > self.boundingRect().height() - 10.0:
                cursor = Qt.SizeFDiagCursor
                self.resize_mode = 'bottom_right'
            else:
                cursor = Qt.SizeHorCursor
                self.resize_mode = 'right'
        else:
            cursor = self.parent.default_cursor
            self.resize_mode = ''
        self.setCursor(cursor)


# pylint: disable=R0904
class HorizontalSymbol(Symbol, object):
    '''
        Class used to handle horizontal symbols
        In case of SDL: INPUT, DECISION answers, Text Symbol, Start
    '''
    def __init__(self, parent=None, text='...',
            x=None, y=None, hyperlink=None):
        super(HorizontalSymbol, self).__init__(parent)
        self.minDistanceToSymbolAbove = 20
        self.connection = None
        if self.has_text_area:
            self.text = EditableText(parent=self, text=text,
                    hyperlink=hyperlink)
        if parent:
            if x and y:
                local_pos = parent.mapFromScene(x, y)
                self.insert_symbol(parent, local_pos.x(), local_pos.y())
            else:
                self.insert_symbol(parent, None, None)
        else:
            self.position = QPointF(x or 0, y or 0)

    def connect_to_parent(self):
        ''' Redefined: connect to parent item '''
        return RakeConnection(self.parent, self)

    def set_valid_pos(self, pos):
        ''' Redefined function - make sure symbol is below its parent '''
        if not self.hasParent:
            super(HorizontalSymbol, self).set_valid_pos(pos)
        else:
            new_y = max(pos.y(), self.parent.boundingRect().height() +
                        self.minDistanceToSymbolAbove)
            self.setPos(pos.x(), new_y)

    def insert_symbol(self, parent, pos_x, pos_y):
        ''' Insert the symbol in the scene - Align below the parent '''
        if not parent:
            self.position = QPointF(pos_x or 0, pos_y or 0)
            return
        super(HorizontalSymbol, self).insert_symbol(parent, pos_x, pos_y)
        if pos_x is None or pos_y is None:
            # Usually for first insertion when item is created:
            # compute position and (if relevant) move siblings
            first, last = None, None
            has_siblings = False
            for sibling in self.siblings():
                has_siblings = True
                first = min(first, sibling.x()) if(
                        first is not None) else sibling.x()
                last = max(last, sibling.x() +
                        sibling.boundingRect().width()) if(
                                last is not None) else(sibling.x() +
                                        sibling.boundingRect().width())
            group_width = last - first if first is not None else 0
            for sibling in self.siblings():
                sib_x = sibling.x() - (self.boundingRect().width()) / 2 - 10
                sib_oldpos = sibling.position
                sibling.pos_x = sib_x
                undo_cmd = undoCommands.MoveSymbol(sibling,
                                                   sib_oldpos,
                                                   sibling.position)
                self.scene().undo_stack.push(undo_cmd)
            most_left = min([sibling.x()
                for sibling in self.siblings()] or [0])
            if has_siblings:
                pos_x = most_left + group_width + 20
            else:
                # Verical alignment (x-axis):
                pos_x = (parent.boundingRect().width() -
                        self.boundingRect().width()) / 2
            pos_y = (parent.boundingRect().height() +
                    self.minDistanceToSymbolAbove)
        self.position = QPointF(pos_x, pos_y)
        self.connection = self.connect_to_parent()
        self.updateConnectionPoints()
        #self.cam(self.position, self.position)

    def update_connections(self):
        '''
           Redefined from Symbol class
           Horizontal symbols may have siblings - check their shape.
        '''
        super(HorizontalSymbol, self).update_connections()
        try:
            for sibling in self.siblings():
                for cnx in sibling.last_branch_item.connections():
                    cnx.reshape()
        except AttributeError:
            pass

    def siblings(self):
        ''' Return all the items's sibling symbols '''
        try:
            return (item for item in self.parent.childItems()
                    if item is not self and isinstance(item, HorizontalSymbol))
            # Don't test only against the same type, that would exclude
            # e.g. Inputs next to Continuous signals
#                   if item is not self and (isinstance(self, type(item)) or
#                       isinstance(item, type(self))))
        except:
            return ()

    def next_aligned_symbol(self):
        ''' Return the next symbol in the flow '''
        for symbol in self.childSymbols():
            if not isinstance(symbol, (HorizontalSymbol, Comment)):
                return symbol
        return None

    def mouse_move(self, event):
        ''' Will prevent move from being above the parent '''
        if self.mode == 'Move':
            event_pos = event.pos()
            new_y = self.pos_y + (event_pos.y() - event.lastPos().y())
            new_x = self.pos_x + (event_pos.x() - event.lastPos().x())
            self.position = QPointF(new_x, new_y)
            self.update_connections()
        super(HorizontalSymbol, self).mouse_move(event)

    def cam(self, old_pos, new_pos, ignore=None):
        '''
            Collision avoidance manoeuvre for parallel branches
            (for SDL: input, decision answers, continuous signals)
        '''
        if self.hasParent:
            # Rectangle of current group of item in scene coordinates
            try:
                # Disconnect the connection below the last item
                # (otherwise the rectangle will be too big)
                last_cnx, = (cnx for cnx in self.last_branch_item.connections()
                        if cnx.child == self.parentItem())
                last_cnx.setParentItem(None)
            except (AttributeError, ValueError):
                last_cnx = None

            rect = (self.sceneBoundingRect() |
                    self.mapRectToScene(self.childrenBoundingRect()))
            try:
                # Set back the last connection
                last_cnx.setParentItem(self.last_branch_item)
            except AttributeError:
                pass
            # Get all siblings (e.g. surrounding inputs/decision answers)
            for sibling in self.siblings():
                try:
                    # Disconnect the connection below the last item
                    last_cnx, = (cnx for cnx in
                            sibling.last_branch_item.connections()
                            if cnx.child == self.parentItem())
                    last_cnx.setParentItem(None)
                except (AttributeError, ValueError):
                    last_cnx = None
                sib_rect = (sibling.sceneBoundingRect() |
                        sibling.mapRectToScene(sibling.childrenBoundingRect()))
                try:
                    # Set back the last connection
                    last_cnx.setParentItem(sibling.last_branch_item)
                except AttributeError:
                    pass
                if rect.intersects(sib_rect):
                    width = (sib_rect & rect).width() + 10
                    old_sib_pos = sibling.position
                    sibling.pos_x += width if self.pos_x <= sibling.pos_x \
                                           else -width
                    undo_cmd = undoCommands.MoveSymbol(sibling,
                                                       old_sib_pos,
                                                       sibling.position)
                    try:
                        self.scene().undo_stack.push(undo_cmd)
                    except AttributeError:
                        # If there is no scene or no undo stack
                        pass
                    sibling.cam(sibling.position, sibling.position)
        super(HorizontalSymbol, self).cam(old_pos, new_pos, ignore)
        # Recursively call the cam of the parent
        try:
            self.parentItem().cam(self.parentItem().position,
                                  self.parentItem().position)
        except AttributeError:
            pass
        self.update_connections()


class VerticalSymbol(Symbol, object):
    '''
        Class used to handle vertically-aligned symbols
        In case of SDL: STATE, OUTPUT, PROCEDURE, DECISION, TASK
    '''
    def __init__(self, parent=None, text='...',
            x=None, y=None, hyperlink=None):
        super(VerticalSymbol, self).__init__(parent)
        self.connection = None
        if self.has_text_area:
            self.text = EditableText(parent=self,
                                     text=text,
                                     hyperlink=hyperlink)
        self.minDistanceToSymbolAbove = 15
        if parent:
            local_pos = self.mapFromScene(0, y or 0)
            self.insert_symbol(parent=parent, x=None, y=local_pos.y())
        else:
            self.position = QPointF(x or 0, y or 0)

    def next_aligned_symbol(self):
        ''' Return the next symbol in the flow '''
        for symbol in self.childSymbols():
            if isinstance(symbol, VerticalSymbol):
                return symbol
        return None

    def connect_to_parent(self):
        ''' Redefined: connect to parent item with a straight line '''
        return VerticalConnection(self.parent, self)

    def set_valid_pos(self, pos):
        ''' Redefined function - make sure symbol is well aligned '''
        if not self.hasParent:
            super(VerticalSymbol, self).set_valid_pos(pos)
        else:
            # 'or self.parent' because of pyside/qt bug
            parent = self.parentItem() or self.parent
            self.setX(-((self.boundingRect().width() -
                      parent.boundingRect().width()) / 2))
            # In case of collision with parent item, move down
            try:
                self.setY(max(pos.y(), parent.connectionPoint.y()))
            except AttributeError:
                self.setY(max(pos.y(), parent.boundingRect().height() + 15))

    def insert_symbol(self, parent, x, y):
        '''
            Vertical symbol: place the symbol in the scene.
            Determine the coordinates based on the position
            and size of the parent item, and make proper connections
        '''
        if not parent:
            # Place standalone item on the scene at given coordinates
            # (e.g. floating state)
            if x is not None and y is not None:
                self.position = QPointF(x, y)
            return
        super(VerticalSymbol, self).insert_symbol(parent, x, y)
        # in a branch (e.g. DECISION) all items must know the first element
        # (used for computing the branch size and the connection point)
        self.branch_entrypoint = parent.branch_entrypoint
        # Check if parent has a connection point (e.g. DECISION)
        # i.e. Check if we are inserting below a decision group
        if hasattr(parent, 'connectionPoint'):
            # Move the new symbol below the connection point:
            # First, check if the parent was the last item of another branch
            for child in parent.childItems():
                if(child not in (self, parent.text, parent.grabber) and not
                        isinstance(child, HorizontalSymbol)):
                    # Insertion: change parent and position of previous child:
                    if (isinstance(child, Connection) and
                            isinstance(child.child, Comment) or
                            isinstance(child, Comment)):
                        continue
                    if not isinstance(child, Connection) or not isinstance(
                            child.child, HorizontalSymbol):
                        child.setParentItem(self)
                        child.parent = self
                        if isinstance(child, Symbol):
                            child_y_diff = (
                                    child.y() -
                                    self.parentItem().connectionPoint.y() +
                                    self.boundingRect().height() +
                                    self.minDistanceToSymbolAbove)
                            child.pos_y = child_y_diff
                            if not isinstance(child, Comment):
                                child.update_position()
        else:
            # If parent already had children,
            # change their parent to the inserted symbol
            for child in parent.childItems():
                if child not in (
                            self, parent.text, parent.comment, parent.grabber):
                    if (isinstance(child, Connection) and
                            isinstance(child.child, Comment)):
                        # Don't change the parent of a comment
                        continue
                    child.parent = self
                    child.setParentItem(self)
                    # move child position down when inserting
                    if isinstance(child, Symbol):
                        child.pos_y = 0.0
                        child.update_position()

        # If inserting an symbol at the end of a branch (e.g. DECISION),
        # inform the branch entry point
        if self.branch_entrypoint and not self.next_aligned_symbol():
            self.branch_entrypoint.last_branch_item = self

        # Create the connection with the parent symbol
        self.connection = self.connect_to_parent()
        self.update_position()
        self.updateConnectionPoints()
        if y is not None:
            self.pos_y = y
        #self.cam(self.position, self.position)

    def mouse_move(self, event):
        ''' Click and move: forbid symbol to move on the x axis '''
        super(VerticalSymbol, self).mouse_move(event)
        if self.mode == 'Move':
            new_y = self.pos_y + event.pos().y() - event.lastPos().y()
            new_x = self.pos_x + event.pos().x() - event.lastPos().x()
            self.position = QPointF(new_x, new_y)
            self.update_connections()
            self.updateConnectionPoints()

    def cam(self, old_pos, new_pos, ignore=None):
        ''' Collision avoidance manoeuvre for vertical symbols '''
        if self.hasParent:
            branch_entry = self
            while branch_entry.hasParent and isinstance(
                    branch_entry, VerticalSymbol):
                # See cam of symbol for explanation about
                # the 'or branch_entry.parent' (pyside/qt bug)
                branch_entry = branch_entry.parentItem() or branch_entry.parent
            branch_entry.cam(branch_entry.position, branch_entry.position)
        else:
            super(VerticalSymbol, self).cam(old_pos, new_pos, ignore)
