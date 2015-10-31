#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Graphical text editing functionalities:
        - Autocompletion
        - Syntax highlighing
        - Automatic placement

    Copyright (c) 2012-2014 European Space Agency

    Designed and implemented by Maxime Perrotin for the TASTE project

    Contact: maxime.perrotin@esa.int
"""

import string
import logging

from PySide.QtCore import Qt, QRegExp, Slot

from PySide.QtGui import(QGraphicsTextItem, QGraphicsProxyWidget, QListWidget,
                         QStringListModel, QCompleter, QListWidgetItem, QFont,
                         QTextCursor, QSyntaxHighlighter, QTextCharFormat,
                         QTextBlockFormat, QStringListModel)

import undoCommands

__all__ = ['EditableText']

LOG = logging.getLogger(__name__)

# pylint: disable=R0904
class Completer(QGraphicsProxyWidget, object):
    ''' Class for handling text autocompletion in the SDL scene '''
    def __init__(self, parent):
        ''' Create an autocompletion list popup '''
        widget = QListWidget()
        super(Completer, self).__init__(parent)
        self.setWidget(widget)
        self.string_list = QStringListModel()
        self._completer = QCompleter()
        self.parent = parent
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        # For some reason the default minimum size is (61,61)
        # Set it to 0 so that the size of the box is not taken
        # into account when it is hidden.
        self.setMinimumSize(0, 0)
        self.prepareGeometryChange()
        self.resize(0, 0)
        self.hide()

    def set_completer_list(self):
        ''' Set list of items for the autocompleter popup '''
        compl = [item.replace('-', '_') for item in
                 self.parent.parentItem().completion_list]
        self.string_list.setStringList(compl)
        self._completer.setModel(self.string_list)

    def set_completion_prefix(self, completion_prefix):
        '''
            Set the current completion prefix (user-entered text)
            and set the corresponding list of words in the popup widget
        '''
        self._completer.setCompletionPrefix(completion_prefix)
        self.widget().clear()
        count = self._completer.completionCount()
        for i in xrange(count):
            self._completer.setCurrentRow(i)
            self.widget().addItem(self._completer.currentCompletion())
        self.prepareGeometryChange()
        if count:
            self.resize(self.widget().sizeHintForColumn(0) + 40, 70)
        else:
            self.resize(0, 0)
        return count

    # pylint: disable=C0103
    def keyPressEvent(self, e):
        super(Completer, self).keyPressEvent(e)
        if e.key() == Qt.Key_Escape:
            self.parentItem().setFocus()
        # Consume the event so that it is not repeated at EditableText level
        e.accept()

    # pylint: disable=C0103
    def focusOutEvent(self, event):
        ''' When the user leaves the popup, return focus to parent '''
        super(Completer, self).focusOutEvent(event)
        self.hide()
        self.resize(0, 0)
        self.parentItem().setFocus()


# pylint: disable=R0904
class Highlighter(QSyntaxHighlighter, object):
    ''' Class for handling syntax highlighting in editable text '''
    def __init__(self, parent, blackbold_patterns, redbold_patterns):
        ''' Define highlighting rules - inputs = lists of patterns '''
        super(Highlighter, self).__init__(parent)
        self.highlighting_rules = []

        # Black bold items (allowed keywords)
        black_bold_format = QTextCharFormat()
        black_bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules = [(QRegExp(pattern, cs=Qt.CaseInsensitive),
            black_bold_format) for pattern in blackbold_patterns]

        # Red bold items (reserved keywords)
        red_bold_format = QTextCharFormat()
        red_bold_format.setFontWeight(QFont.Bold)
        red_bold_format.setForeground(Qt.red)
        for pattern in redbold_patterns:
            self.highlighting_rules.append(
                    (QRegExp(pattern, cs=Qt.CaseInsensitive), red_bold_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.darkBlue)
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp('--[^\n]*'), comment_format))

    # pylint: disable=C0103
    def highlightBlock(self, text):
        ''' Redefined function to apply the highlighting rules '''
        for expression, formatter in self.highlighting_rules:
            index = expression.indexIn(text)
            while (index >= 0):
                length = expression.matchedLength()
                self.setFormat(index, length, formatter)
                index = expression.indexIn(text, index + length)


# pylint: disable=R0902
class EditableText(QGraphicsTextItem, object):
    '''
        Editable text area inside symbols
        Includes autocompletion when parent item needs it
    '''
    default_cursor = Qt.IBeamCursor
    hasParent = False

    def __init__(self, parent, text='...', hyperlink=None):
        super(EditableText, self).__init__(parent)
        self.parent = parent
        self.setFont(QFont('Ubuntu', 10))
        self.completer = Completer(self)
        self.completer.widget().itemActivated.connect(
                self.completion_selected)
        self.hyperlink = hyperlink
        self.setOpenExternalLinks(True)
        if hyperlink:
            self.setHtml('<a href="{hlink}">{text}</a>'.format
                    (hlink=hyperlink, text=text.replace('\n', '<br>')))
        else:
            self.setPlainText(text)
        self.setTextInteractionFlags(Qt.TextEditorInteraction
                                     | Qt.LinksAccessibleByMouse
                                     | Qt.LinksAccessibleByKeyboard)
        self.completer_has_focus = False
        self.editing = False
        self.try_resize()
        self.highlighter = Highlighter(
                self.document(), parent.blackbold, parent.redbold)
        self.completion_prefix = ''
        self.set_textbox_position()
        self.set_text_alignment()
        # Increase the Z value of the text area so that the autocompleter
        # always appear on top of text's siblings (parents's followers)
        self.setZValue(self.zValue() + 1)
        # context is used for advanced autocompletion
        self.context = ''
        # Set cursor when mouse goes over the text
        self.setCursor(self.default_cursor)
        # Activate cache mode to boost rendering by calling paint less often
        # Removed - does not render text properly (eats up the right part)
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def set_text_alignment(self):
        ''' Apply the required text alignment within the text box '''
        alignment = self.parent.text_alignment
        self.setTextWidth(self.boundingRect().width())
        fmt = QTextBlockFormat()
        fmt.setAlignment(alignment)
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def set_textbox_position(self):
        ''' Compute the textbox position '''
        parent_rect = self.parent.boundingRect()
        rect = self.boundingRect()
        # Use parent symbol alignment requirement
        # Does not support right nor bottom alignment
        alignment = self.parent.textbox_alignment
        rect_center = parent_rect.center() - rect.center()
        if alignment & Qt.AlignLeft:
            x_pos = 0
        elif alignment & Qt.AlignHCenter:
            x_pos = rect_center.x()
        if alignment & Qt.AlignTop:
            y_pos = 0
        elif alignment & Qt.AlignVCenter:
            y_pos = rect_center.y()
        self.setPos(x_pos, y_pos)

    def paint(self, painter, _, ___):
        ''' Place the textbox in the parent symbol and draw it '''
        self.set_textbox_position()
        super(EditableText, self).paint(painter, _, ___)

    def try_resize(self):
        '''
            If needed, request a resizing of the parent item
            (when text size expands)
        '''
        if self.parent.auto_expand:
            self.setTextWidth(-1)
            parent_rect = self.parent.boundingRect()
            rect = self.boundingRect()
            if rect.width() + 30 > parent_rect.width():
                parent_rect.setWidth(rect.width() + 30)
            parent_rect.setHeight(max(rect.height(), parent_rect.height()))
            self.parent.resize_item(parent_rect)

    @Slot(QListWidgetItem)
    def completion_selected(self, item):
        '''
            Slot connected to the autocompletion popup,
            invoked when selection is made
        '''
        if not(self.textInteractionFlags() & Qt.TextEditable):
            self.completer.hide()
            return
        text_cursor = self.textCursor()
        # Go back to the previously saved cursor position
        text_cursor.setPosition(self.cursor_position)
        extra = len(item.text()) - len(self.completion_prefix)
        if extra > 0:
            if len(self.completion_prefix):
                # Move back left only if there is a word to replace
                text_cursor.movePosition(QTextCursor.Left)
                text_cursor.movePosition(QTextCursor.EndOfWord)
            text_cursor.insertText(item.text()[-extra:])
            self.setTextCursor(text_cursor)
        self.completer_has_focus = False
        self.completer.hide()
        self.try_resize()


    def context_completion_list(self, force=False):
        ''' Advanced context-dependent autocompletion '''
        # Select text from the begining of a line to the cursor position
        # Then keep the last word including separators ('!' and '.')
        # This word (e.g. variable!field!subfield) is then used to update
        # the autocompletion list.
        cursor = self.textCursor()
        pos = cursor.positionInBlock() - 1
        cursor.select(QTextCursor.BlockUnderCursor)
        context = self.context
        try:
            # If not the first line of the text, Qt adds u+2029 as 1st char
            line = cursor.selectedText().replace(u'\u2029', '')
            if line[pos] in string.ascii_letters + '!' + '.' + '_':
                self.context = line[slice(0, pos + 1)].split()[-1]
            else:
                self.context = ''
        except IndexError:
            pass
        if (context != self.context) or force:
            self.completer.set_completer_list()


    # pylint: disable=C0103
    def keyPressEvent(self, event):
        '''
            Activate the autocompletion window if relevant
        '''
        super(EditableText, self).keyPressEvent(event)
        # Typing Esc allows to stop editing text:
        if event.key() == Qt.Key_Escape:
            self.clearFocus()
            return
        # When completer is displayed, give it the focus with down key
        if self.completer.isVisible() and event.key() == Qt.Key_Down:
            self.completer_has_focus = True
            self.completer.setFocusProxy(None)
            self.completer.widget().setFocus()
            return
        self.try_resize()
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        self.completion_prefix = text_cursor.selectedText()

        self.context_completion_list(force=(event.key()==Qt.Key_F8))

        completion_count = self.completer.set_completion_prefix(
                self.completion_prefix)
        if(completion_count > 0 and len(self.completion_prefix) > 1) or(
                event.key() == Qt.Key_F8):
            # Save the position of the cursor
            self.cursor_position = self.textCursor().position()
            # Computing the coordinates of the completer
            # No direct Qt function for that.. doing it the hard way
            pos = self.textCursor().positionInBlock()
            block = self.textCursor().block()
            layout = block.layout()
            line = layout.lineForTextPosition(pos)
            rect = line.rect()
            relative_x, _ = line.cursorToX(pos)
            layout_pos = layout.position()
            pos_x = relative_x + layout_pos.x()
            pos_y = rect.y() + rect.height() + layout_pos.y()

            self.completer.setPos(pos_x, pos_y)
            self.completer.show()
            # Make sure parent item has higher visibility than its siblings
            # (useful in decision branches)
            self.parent.setZValue(1)
            self.completer.setFocusProxy(self)
            self.setTabChangesFocus(True)
        else:
            self.completer.setFocusProxy(None)
            self.completer.hide()
            self.completer.resize(0, 0)
            self.setFocus()
        self.completer_has_focus = False

    # pylint: disable=C0103
    def focusOutEvent(self, event):
        '''
            When the user stops editing, this function is called
            In that case, hide the completer if it is not the item
            that got the focus.
        '''
        if not self.editing:
            return super(EditableText, self).focusOutEvent(event)
        if self.completer and not self.completer_has_focus:
            self.completer.hide()
            self.completer.resize(0, 0)
        if not self.completer or not self.completer.isVisible():
            # Trigger a select - side effect makes the toolbar update
            try:
                self.parent.select(True)
            except AttributeError:
                # Some parents may not be selectable (e.g. Signalroute)
                pass
            self.editing = False
            text_cursor = self.textCursor()
            if text_cursor.hasSelection():
                text_cursor.clearSelection()
                self.setTextCursor(text_cursor)
            # If something has changed, check syntax and create undo command
            if(self.oldSize != self.parent.boundingRect() or
                                                self.oldText != unicode(self)):
                # Call syntax checker from item containing the text (if any)
                self.scene().check_syntax(self.parent)
                # Update class completion list
                self.scene().update_completion_list(self.parentItem())
                # Create undo command, including possible CAM
                with undoCommands.UndoMacro(self.scene().undo_stack, 'Text'):
                    undo_cmd = undoCommands.ResizeSymbol(
                                          self.parent, self.oldSize,
                                          self.parent.boundingRect())
                    self.scene().undo_stack.push(undo_cmd)
                    try:
                        self.parent.cam(self.parent.pos(),
                                              self.parent.pos())
                    except AttributeError:
                        # Some parents may not have CAM function (e.g. Channel)
                        pass

                    undo_cmd = undoCommands.ReplaceText(self, self.oldText,
                                                        unicode(self))
                    self.scene().undo_stack.push(undo_cmd)
        self.set_text_alignment()
        # Reset Z-Values that were increased when getting focus
        top_level = self.parent.top_level()
        top_level.setZValue(top_level.zValue() - 1)
        self.parent.setZValue(self.parent.zValue() - 1)
        super(EditableText, self).focusOutEvent(event)

    # pylint: disable=C0103
    def focusInEvent(self, event):
        ''' When user starts editing text, save previous state for Undo '''
        super(EditableText, self).focusInEvent(event)
        # Change the Z-value of items to make sure the
        # completer is always be on top of other symbols
        top_level = self.parent.top_level()
        top_level.setZValue(top_level.zValue() + 1)
        self.parent.setZValue(self.parent.zValue() + 1)

        # Trigger a select - side effect makes the toolbar update
        try:
            self.parent.select(True)
        except AttributeError:
            # Some parents may not be selectable (e.g. Signalroute)
            pass
        # Update completer list of keywords
        self.context = ''
        self.completer.set_completer_list()
        # Clear selection otherwise the "Delete" key may delete other items
        self.scene().clearSelection()
        # Set width to auto-expand, and disables alignment, while editing:
        self.setTextWidth(-1)
        if not self.editing:
            self.oldText = unicode(self)
            self.oldSize = self.parent.boundingRect()
            self.editing = True

    def __str__(self):
        ''' Print the text inside the symbol '''
        raise TypeError('Use UNICODE, not string!')

    def __unicode__(self):
        return self.toPlainText()


