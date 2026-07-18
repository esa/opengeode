# -*- coding: utf-8 -*-

"""
    OpenGEODE - ASN.1 File Editor extension
    Provides syntax highlighting, line numbers, autocompletion, LSP diagnostics,
    and a toggleable Vim mode for ASN.1 files.
"""

import os
import json
import subprocess
import threading
from PySide6.QtWidgets import QPlainTextEdit, QCompleter, QWidget, QTextEdit, QLineEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor, QKeyEvent, QPainter, QTextFormat, QTextDocument
from PySide6.QtCore import Qt, QRegularExpression, QStringListModel, QRect, QSize, QObject, Signal

class ASN1Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords: bold and blue
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r"\bBEGIN\b", r"\bEND\b", r"\bDEFINITIONS\b", r"\bIMPORTS\b", r"\bEXPORTS\b",
            r"\bFROM\b", r"\bCHOICE\b", r"\bSEQUENCE\b", r"\bOF\b", r"\bINTEGER\b",
            r"\bBOOLEAN\b", r"\bOCTET\b", r"\bSTRING\b", r"\bREAL\b", r"\bENUMERATED\b",
            r"\bSIZE\b", r"\bWITH\b", r"\bCOMPONENTS\b", r"\bTRUE\b", r"\bFALSE\b",
            r"\bIA5String\b", r"\bNumericString\b", r"\bVisibleString\b", r"\bUTCTime\b",
            r"\bGeneralizedTime\b"
        ]
        for pattern in keywords:
            self.highlighting_rules.append((
                QRegularExpression(pattern), keyword_format
            ))

        # Types (Uppercase identifiers): bold and teal
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#008080"))
        type_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((
            QRegularExpression(r"\b[A-Z][a-zA-Z0-9_-]*\b"), type_format
        ))

        # Comments (-- to end of line or another --): italic and green
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r"--[^\n]*"), comment_format
        ))

        # Strings: dark red
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A31515"))
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"\n]*"'), string_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"'[0-9A-Fa-f]+'H"), string_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"'[01]+'B"), string_format
        ))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class VimLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.clear()
            if self.parentWidget():
                self.parentWidget().hide()
            main_win = self.window()
            if hasattr(main_win, 'asn1_editor') and main_win.asn1_editor:
                main_win.asn1_editor.setFocus()
                main_win.asn1_editor.set_vim_state("NORMAL")
            e.accept()
            return
        super().keyPressEvent(e)


class ASN1TextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer = None
        self.error_lines = set()
        
        # Vim mode properties
        self.vim_mode_enabled = False
        self.vim_state = "NORMAL" # NORMAL, INSERT, VISUAL, PENDING
        self.vim_pending_key = None
        self.yank_buffer = ""
        self.yank_is_line = False
        self.visual_anchor_cursor = None
        self.indent_size = 3
        self.last_search_pattern = ""
        self.vim_count = ""
        self.vim_pending_count = ""
        self.last_edit_action = None
        self.vim_insert_trigger = ""
        self.is_recording_insert = False
        self.last_insert_text = ""
        self.insert_start_pos = 0
        
        self.setFont(QFont('UbuntuMono', 12))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Line number area setup
        self.lineNumberArea = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLineAndErrors)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLineAndErrors()

    def setCompleter(self, completer):
        if self._completer:
            self._completer.activated.disconnect()
        
        self._completer = completer
        if not self._completer:
            return
            
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer:
            self._completer.setWidget(self)
        super().focusInEvent(e)

    def event(self, e):
        from PySide6.QtCore import QEvent
        if e.type() == QEvent.ShortcutOverride:
            if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_N:
                e.accept()
                return True
        return super().event(e)

    def keyPressEvent(self, e: QKeyEvent):
        # 1. If completer popup is visible, handle selection override first
        if self._completer and self._completer.popup().isVisible():
            if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_N:
                popup = self._completer.popup()
                current_row = popup.currentIndex().row()
                next_row = (current_row + 1) % popup.model().rowCount()
                popup.setCurrentIndex(popup.model().index(next_row, 0))
                e.accept()
                return
            if e.key() == Qt.Key_Escape:
                if self.vim_mode_enabled:
                    self.set_vim_state("NORMAL")
                self._completer.popup().hide()
                e.accept()
                return
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        # 2. If Vim mode is enabled and we are not in INSERT mode, handle keys via Vim emulation
        if self.vim_mode_enabled and self.vim_state != "INSERT":
            # Handle REPLACE state
            if self.vim_state == "REPLACE":
                if e.key() == Qt.Key_Escape:
                    self.set_vim_state("NORMAL")
                    e.accept()
                    return
                char = e.text()
                if char and len(char) == 1 and char not in ("\r", "\n"):
                    has_count = bool(self.vim_count)
                    count = int(self.vim_count) if has_count else 1
                    self.vim_count = ""
                    
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, count)
                    cursor.insertText(char * count)
                    self.setTextCursor(cursor)
                    
                    self.last_edit_action = { 'type': 'r', 'char': char, 'count': count }
                    self.set_vim_state("NORMAL")
                    e.accept()
                    return
                # Ignore non-character control keys in replace mode
                return

            key = e.key()
            
            # Universal Escape to Normal Mode
            if key == Qt.Key_Escape:
                cursor = self.textCursor()
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.set_vim_state("NORMAL")
                e.accept()
                return
                
            # Allow arrow keys to navigate even in NORMAL/VISUAL mode
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if self.vim_state == "VISUAL":
                    self.handle_visual_mode_key(e)
                else:
                    self.handle_normal_mode_key(e)
                e.accept()
                return
                
            if self.vim_state == "VISUAL":
                self.handle_visual_mode_key(e)
            elif self.vim_state == "PENDING":
                self.handle_pending_mode_key(e)
            else:
                self.handle_normal_mode_key(e)
            e.accept()
            return

        # 2. Escape from INSERT mode back to NORMAL mode
        if self.vim_mode_enabled and self.vim_state == "INSERT" and e.key() == Qt.Key_Escape:
            self.set_vim_state("NORMAL")
            e.accept()
            return

        # Auto-dedent on typing closing brackets/parentheses
        if not self.vim_mode_enabled or self.vim_state == "INSERT":
            if e.text() in ('}', ')', ']'):
                cursor = self.textCursor()
                block = cursor.block()
                line_text = block.text()
                col = cursor.positionInBlock()
                prefix = line_text[:col]
                if prefix.strip() == "":
                    dedent_size = min(len(prefix), self.indent_size)
                    if dedent_size > 0:
                        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, dedent_size)
                        cursor.removeSelectedText()
                        cursor.insertText(e.text())
                        self.setTextCursor(cursor)
                        e.accept()
                        return

        # Auto-indent on pressing Enter/Return
        if not self.vim_mode_enabled or self.vim_state == "INSERT":
            if e.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.perform_auto_indent()
                e.accept()
                return



        if e.key() == Qt.Key_Tab:
            self.insertPlainText(" " * self.indent_size)
            return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) and e.key() in (Qt.Key_E, Qt.Key_N))
        if not self._completer or not isShortcut:
            super().keyPressEvent(e)

        if self.vim_mode_enabled and self.vim_state == "INSERT" and not isShortcut:
            if self._completer and not self._completer.popup().isVisible():
                self._completer.popup().hide()
                return

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if not self._completer or (ctrlOrShift and e.text() == "" and not isShortcut):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        
        # Dynamically harvest buffer words and update completer model
        self.update_completer_words()
        
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or e.text() == "" or len(completionPrefix) < 2 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        # Only display the autocompletion box when there is an actual match to autocomplete
        if not isShortcut:
            count = self._completer.completionCount()
            if count == 0:
                self._completer.popup().hide()
                return
            elif count == 1 and self._completer.currentCompletion().lower() == completionPrefix.lower():
                self._completer.popup().hide()
                return

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)

    def inputMethodEvent(self, event):
        if self.vim_mode_enabled and self.vim_state != "INSERT":
            commit_text = event.commitString()
            if commit_text:
                for char in commit_text:
                    from PySide6.QtGui import QKeyEvent
                    from PySide6.QtCore import QEvent
                    key_evt = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, char)
                    self.keyPressEvent(key_evt)
            event.accept()
            return
        super().inputMethodEvent(event)

    # Vim Mode State Machine
    def set_vim_state(self, state):
        if self.vim_state == "INSERT" and state == "NORMAL":
            self.exit_insert_mode()
            
        self.vim_state = state
        if state in ("NORMAL", "INSERT"):
            self.vim_pending_key = None
            self.vim_count = ""
            self.vim_pending_count = ""
            
        if state == "INSERT":
            self.insert_start_pos = self.textCursor().position()
            self.is_recording_insert = True
            self.last_insert_text = ""
            
        main_win = self.window()
        if hasattr(main_win, 'update_vim_status'):
            main_win.update_vim_status(state)

    def exit_insert_mode(self):
        if self.is_recording_insert:
            self.is_recording_insert = False
            start = min(self.insert_start_pos, self.textCursor().position())
            end = max(self.insert_start_pos, self.textCursor().position())
            cursor = self.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            self.last_insert_text = cursor.selectedText()
            self.last_insert_text = self.last_insert_text.replace("\u2029", "\n")
            
            if self.vim_insert_trigger == 'cw':
                self.last_edit_action = {
                    'type': 'cw',
                    'count': 1,
                    'text': self.last_insert_text
                }
            else:
                self.last_edit_action = {
                    'type': 'insert',
                    'trigger': self.vim_insert_trigger,
                    'text': self.last_insert_text
                }

    def handle_normal_mode_key(self, e):
        text = e.text()
        key = e.key()
        
        # Ignore modifier keys alone
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta, Qt.Key_AltGr, Qt.Key_CapsLock):
            return
            
        # Check if key is a digit for count prefix
        if text.isdigit():
            if text == '0' and not self.vim_count:
                # '0' without a count prefix is a movement command (start of line)
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.StartOfLine)
                self.setTextCursor(cursor)
                return
            else:
                self.vim_count += text
                return
                
        # Non-digit: consume the accumulated count prefix
        has_count = bool(self.vim_count)
        count = int(self.vim_count) if has_count else 1
        
        # We only clear self.vim_count here if this is NOT a pending trigger
        # (since pending commands like "d", "y" need the count inside PENDING state)
        if text not in ('d', 'y', 'g', 'c', 'f', '<', '>', 'r'):
            self.vim_count = ""
            
        # Check Ctrl-R for Redo
        if e.modifiers() == Qt.ControlModifier and key == Qt.Key_R:
            self.vim_count = ""
            for _ in range(count):
                self.redo()
            return

        # Movements
        if text == 'h' or key == Qt.Key_Left:
            for _ in range(count):
                self.moveCursor(QTextCursor.Left)
        elif text == 'j' or key == Qt.Key_Down:
            for _ in range(count):
                self.moveCursor(QTextCursor.Down)
        elif text == 'k' or key == Qt.Key_Up:
            for _ in range(count):
                self.moveCursor(QTextCursor.Up)
        elif text == 'l' or key == Qt.Key_Right:
            for _ in range(count):
                self.moveCursor(QTextCursor.Right)
        elif text == '{':
            self.vim_paragraph_backward(count=count, keep_anchor=False)
        elif text == '}':
            self.vim_paragraph_forward(count=count, keep_anchor=False)
        elif text == '(':
            self.vim_sentence_backward(count=count, keep_anchor=False)
        elif text == ')':
            self.vim_sentence_forward(count=count, keep_anchor=False)
            
        # Entering other modes
        elif text == 'i':
            self.vim_insert_trigger = 'i'
            self.set_vim_state("INSERT")
        elif text == 'a':
            self.vim_insert_trigger = 'a'
            self.moveCursor(QTextCursor.Right)
            self.set_vim_state("INSERT")
        elif text == 'o':
            self.vim_insert_trigger = 'o'
            cursor = self.textCursor()
            indent = self.get_indentation_for_new_line(cursor.block())
            cursor.movePosition(QTextCursor.EndOfLine)
            for _ in range(count):
                cursor.insertText("\n" + indent)
            self.setTextCursor(cursor)
            self.set_vim_state("INSERT")
        elif text == 'O':
            self.vim_insert_trigger = 'O'
            cursor = self.textCursor()
            indent = self.get_indentation_for_new_line(cursor.block())
            cursor.movePosition(QTextCursor.StartOfLine)
            for _ in range(count):
                cursor.insertText(indent + "\n")
            cursor.movePosition(QTextCursor.Up)
            self.setTextCursor(cursor)
            self.set_vim_state("INSERT")
        elif text == 'v':
            self.set_vim_state("VISUAL")
            # Store visual anchor cursor
            self.visual_anchor_cursor = self.textCursor()
            
        # Commands
        elif text == 'u':
            for _ in range(count):
                self.undo()
        elif text == 'p':
            for _ in range(count):
                self.vim_paste()
        elif text == 'x':
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, count)
            self.yank_buffer = cursor.selectedText()
            self.yank_is_line = False
            cursor.removeSelectedText()
            self.setTextCursor(cursor)
            self.last_edit_action = { 'type': 'x', 'count': count }
        elif text == '.':
            if self.last_edit_action:
                action = self.last_edit_action
                repeat_count = count if has_count else action.get('count', 1)
                
                if action['type'] == 'insert':
                    trigger = action.get('trigger', 'i')
                    insert_text = action.get('text', '')
                    if trigger == 'i':
                        cursor = self.textCursor()
                        for _ in range(repeat_count):
                            cursor.insertText(insert_text)
                        self.setTextCursor(cursor)
                    elif trigger == 'a':
                        self.moveCursor(QTextCursor.Right)
                        cursor = self.textCursor()
                        for _ in range(repeat_count):
                            cursor.insertText(insert_text)
                        self.setTextCursor(cursor)
                    elif trigger == 'o':
                        cursor = self.textCursor()
                        indent = self.get_indentation_for_new_line(cursor.block())
                        cursor.movePosition(QTextCursor.EndOfLine)
                        for _ in range(repeat_count):
                            cursor.insertText("\n" + indent + insert_text)
                        self.setTextCursor(cursor)
                    elif trigger == 'O':
                        cursor = self.textCursor()
                        indent = self.get_indentation_for_new_line(cursor.block())
                        cursor.movePosition(QTextCursor.StartOfLine)
                        for _ in range(repeat_count):
                            cursor.insertText(indent + insert_text + "\n")
                        cursor.movePosition(QTextCursor.Up)
                        self.setTextCursor(cursor)
                elif action['type'] == 'dd':
                    self.vim_delete_line(count=repeat_count)
                elif action['type'] == 'dw':
                    self.vim_delete_word(count=repeat_count)
                elif action['type'] == 'cw':
                    self.vim_delete_word(count=repeat_count)
                    cursor = self.textCursor()
                    cursor.insertText(action.get('text', ''))
                    self.setTextCursor(cursor)
                elif action['type'] in ('df', 'dt'):
                    self.vim_delete_to_char(action['char'], include_char=(action['type'] == 'df'), count=repeat_count)
                elif action['type'] == 'x':
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, repeat_count)
                    cursor.removeSelectedText()
                    self.setTextCursor(cursor)
                elif action['type'] == 'r':
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, repeat_count)
                    cursor.insertText(action['char'] * repeat_count)
                    self.setTextCursor(cursor)
                elif action['type'] == '<':
                    self.vim_shift_left(count=repeat_count)
                elif action['type'] == '>':
                    self.vim_shift_right(count=repeat_count)
                elif action['type'] == 'case':
                    if action['target'] == 'line':
                        self.vim_change_case_lines(action['mode'], count=repeat_count)
                    elif action['target'] == 'word':
                        self.vim_change_case_words(action['mode'], count=repeat_count)
                elif action['type'] == '~':
                    self.vim_toggle_case(count=repeat_count)
        elif text == 'G':
            if has_count:
                cursor = self.textCursor()
                target_block = max(0, count - 1)
                target_block = min(target_block, self.document().blockCount() - 1)
                block = self.document().findBlockByNumber(target_block)
                cursor.setPosition(block.position())
                self.setTextCursor(cursor)
            else:
                self.moveCursor(QTextCursor.End)
        elif text == 'n':
            for _ in range(count):
                self.search_forward(self.last_search_pattern)
        elif text == 'N':
            for _ in range(count):
                self.search_backward(self.last_search_pattern)
        elif text == '*':
            word = self.textUnderCursor()
            if word:
                self.last_search_pattern = word
                self.search_forward(word)
                for _ in range(count - 1):
                    self.search_forward(word)
        elif text == '#':
            word = self.textUnderCursor()
            if word:
                self.last_search_pattern = word
                self.search_backward(word)
                for _ in range(count - 1):
                    self.search_backward(word)
            
        # Pending triggers: d, y, g, c, f, <, >
        elif text in ('d', 'y', 'g', 'c', 'f', '<', '>'):
            self.vim_pending_key = text
            self.set_vim_state("PENDING")
        elif text == 'r':
            self.set_vim_state("REPLACE")
        elif text == '~':
            self.vim_toggle_case(count=count)
            self.last_edit_action = { 'type': '~', 'count': count }
            
        # Command line mode triggers
        elif text == ':':
            main_win = self.window()
            if hasattr(main_win, 'show_vim_input'):
                main_win.show_vim_input(":")
        elif text == '/':
            main_win = self.window()
            if hasattr(main_win, 'show_vim_input'):
                main_win.show_vim_input("/")

    def setPlainText(self, text):
        super().setPlainText(text)
        self.indent_size = self.detect_indent_size()

    def detect_indent_size(self):
        text = self.toPlainText()
        lines = text.splitlines()
        space_counts = []
        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                continue
            count = len(line) - len(stripped)
            if count > 0:
                space_counts.append(count)
        if not space_counts:
            return 3
        diffs = []
        for i in range(1, len(space_counts)):
            d = abs(space_counts[i] - space_counts[i-1])
            if d > 0 and d <= 8:
                diffs.append(d)
        if diffs:
            from collections import Counter
            most_common = Counter(diffs).most_common(1)
            if most_common:
                return most_common[0][0]
        from collections import Counter
        most_common = Counter(space_counts).most_common(1)
        if most_common:
            val = most_common[0][0]
            for c in (4, 3, 2, 8):
                if val % c == 0:
                    return c
            return val
        return 3

    def get_indentation_for_new_line(self, block):
        line_text = block.text()
        leading_spaces_count = len(line_text) - len(line_text.lstrip(' '))
        indent = " " * leading_spaces_count
        stripped_line = line_text.strip()
        if stripped_line and stripped_line[-1] in ('{', '(', '['):
            indent += " " * self.indent_size
        return indent

    def perform_auto_indent(self):
        cursor = self.textCursor()
        block = cursor.block()
        line_text = block.text()
        col = cursor.positionInBlock()
        
        prefix = line_text[:col]
        suffix = line_text[col:]
        
        leading_spaces_count = len(prefix) - len(prefix.lstrip(' '))
        indent = " " * leading_spaces_count
        
        stripped_prefix = prefix.strip()
        increase_indent = False
        if stripped_prefix and stripped_prefix[-1] in ('{', '(', '['):
            increase_indent = True
            
        if increase_indent:
            indent += " " * self.indent_size
            
        stripped_suffix = suffix.strip()
        if increase_indent and stripped_suffix and stripped_suffix[0] in ('}', ')', ']'):
            cursor.insertText("\n" + indent + "\n" + (" " * leading_spaces_count))
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.EndOfLine)
            self.setTextCursor(cursor)
            return
            
        cursor.insertText("\n" + indent)
        self.setTextCursor(cursor)

    def update_completer_words(self):
        if not self._completer:
            return
        model = self._completer.model()
        existing_words = []
        if model:
            if hasattr(model, 'stringList'):
                existing_words = list(model.stringList())
            else:
                for r in range(model.rowCount()):
                    existing_words.append(model.data(model.index(r, 0)))
        import re
        content = self.toPlainText()
        buffer_words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_-]*\b', content)
        all_words = sorted(list(set(existing_words + buffer_words)))
        if model and hasattr(model, 'setStringList'):
            model.setStringList(all_words)
        else:
            new_model = QStringListModel(all_words, self._completer)
            self._completer.setModel(new_model)

    def search_forward(self, pattern):
        if not pattern:
            return
        cursor = self.document().find(pattern, self.textCursor())
        if not cursor.isNull():
            self.setTextCursor(cursor)
        else:
            cursor = self.document().find(pattern, 0)
            if not cursor.isNull():
                self.setTextCursor(cursor)
            else:
                main_win = self.window()
                if hasattr(main_win, 'statusBar'):
                    main_win.statusBar().showMessage(f"Pattern not found: {pattern}", 3000)

    def search_backward(self, pattern):
        if not pattern:
            return
        cursor = self.document().find(pattern, self.textCursor(), QTextDocument.FindBackward)
        if not cursor.isNull():
            self.setTextCursor(cursor)
        else:
            end_cursor = self.textCursor()
            end_cursor.movePosition(QTextCursor.End)
            cursor = self.document().find(pattern, end_cursor, QTextDocument.FindBackward)
            if not cursor.isNull():
                self.setTextCursor(cursor)
            else:
                main_win = self.window()
                if hasattr(main_win, 'statusBar'):
                    main_win.statusBar().showMessage(f"Pattern not found: {pattern}", 3000)

    def handle_pending_mode_key(self, e):
        text = e.text()
        key = e.key()
        
        # Ignore modifier keys alone
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta, Qt.Key_AltGr, Qt.Key_CapsLock):
            return
            
        # Accumulate count if digit is typed in pending state
        if text.isdigit():
            self.vim_pending_count += text
            self.set_vim_state("PENDING")
            return
            
        first = self.vim_pending_key
        
        # If first is 'd' and user presses 'f' or 't', wait for target char
        if first == 'd' and text in ('f', 't'):
            self.vim_pending_key = 'd' + text
            self.set_vim_state("PENDING")
            return
            
        # If first is 'g' and user presses 'u' or 'U', wait for target char/motion
        if first == 'g' and text in ('u', 'U'):
            self.vim_pending_key = 'g' + text
            self.set_vim_state("PENDING")
            return
            
        # Combine counts
        count = 1
        if self.vim_count:
            count *= int(self.vim_count)
        if self.vim_pending_count:
            count *= int(self.vim_pending_count)
            
        self.set_vim_state("NORMAL") # Reset by default
        
        if first == 'd' and text == 'd':
            self.vim_delete_line(count=count)
            self.last_edit_action = { 'type': 'dd', 'count': count }
        elif first == 'd' and text == 'w':
            self.vim_delete_word(count=count)
            self.last_edit_action = { 'type': 'dw', 'count': count }
        elif first == 'y' and text == 'y':
            self.vim_yank_line(count=count)
        elif first == 'g' and text == 'g':
            cursor = self.textCursor()
            target_block = max(0, count - 1)
            target_block = min(target_block, self.document().blockCount() - 1)
            block = self.document().findBlockByNumber(target_block)
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)
        elif first == 'c' and text == 'w':
            self.vim_insert_trigger = 'cw'
            self.vim_delete_word(count=count)
            self.set_vim_state("INSERT")
        elif first == 'f' and len(text) == 1:
            self.vim_find_char(text, count=count)
        elif (first == 'df' or first == 'dt') and len(text) == 1:
            self.vim_delete_to_char(text, include_char=(first == 'df'), count=count)
            self.last_edit_action = { 'type': first, 'char': text, 'count': count }
        elif first == '<' and text == '<':
            self.vim_shift_left(count=count)
            self.last_edit_action = { 'type': '<', 'count': count }
        elif first == '>' and text == '>':
            self.vim_shift_right(count=count)
            self.last_edit_action = { 'type': '>', 'count': count }
        elif first in ('gu', 'gU'):
            if text == first[-1:]:
                self.vim_change_case_lines(mode=first, count=count)
                self.last_edit_action = { 'type': 'case', 'mode': first, 'target': 'line', 'count': count }
            elif text == 'w':
                self.vim_change_case_words(mode=first, count=count)
                self.last_edit_action = { 'type': 'case', 'mode': first, 'target': 'word', 'count': count }

    def handle_visual_mode_key(self, e):
        text = e.text()
        key = e.key()
        cursor = self.textCursor()
        
        # Handle visual pending 'g' key
        if self.vim_pending_key == 'g':
            self.vim_pending_key = None
            if text == 'u':
                if cursor.hasSelection():
                    selected_text = cursor.selectedText()
                    cursor.insertText(selected_text.lower())
                self.set_vim_state("NORMAL")
                self.setTextCursor(cursor)
                return
            elif text == 'U':
                if cursor.hasSelection():
                    selected_text = cursor.selectedText()
                    cursor.insertText(selected_text.upper())
                self.set_vim_state("NORMAL")
                self.setTextCursor(cursor)
                return

        if text == 'g':
            self.vim_pending_key = 'g'
            return
            
        if text == 'h' or key == Qt.Key_Left:
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
        elif text == 'j' or key == Qt.Key_Down:
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        elif text == 'k' or key == Qt.Key_Up:
            cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
        elif text == 'l' or key == Qt.Key_Right:
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        elif text == 'G':
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        elif text == '{':
            self.vim_paragraph_backward(count=1, keep_anchor=True)
            return
        elif text == '}':
            self.vim_paragraph_forward(count=1, keep_anchor=True)
            return
        elif text == '(':
            self.vim_sentence_backward(count=1, keep_anchor=True)
            return
        elif text == ')':
            self.vim_sentence_forward(count=1, keep_anchor=True)
            return
            
        # Editing commands in Visual Mode
        elif text == 'd':
            if cursor.hasSelection():
                self.yank_buffer = cursor.selectedText()
                self.yank_is_line = False
                cursor.removeSelectedText()
            self.set_vim_state("NORMAL")
        elif text == 'y':
            if cursor.hasSelection():
                self.yank_buffer = cursor.selectedText()
                self.yank_is_line = False
            cursor.clearSelection()
            self.set_vim_state("NORMAL")
        elif text == 'u':
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                cursor.insertText(selected_text.lower())
            self.set_vim_state("NORMAL")
        elif text == 'U':
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                cursor.insertText(selected_text.upper())
            self.set_vim_state("NORMAL")
        elif text == '~':
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                toggled_chars = []
                for char in selected_text:
                    if char.islower():
                        toggled_chars.append(char.upper())
                    elif char.isupper():
                        toggled_chars.append(char.lower())
                    else:
                        toggled_chars.append(char)
                cursor.insertText("".join(toggled_chars))
            self.set_vim_state("NORMAL")
        elif text == 'i':
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.vim_insert_trigger = 'i'
            self.set_vim_state("INSERT")
            return
        elif text in ('>', '<'):
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                start_block = self.document().findBlock(start).blockNumber()
                end_block = self.document().findBlock(end).blockNumber()
                
                for i in range(start_block, end_block + 1):
                    block = self.document().findBlockByNumber(i)
                    if not block.isValid():
                        continue
                    block_cursor = QTextCursor(block)
                    if text == '>':
                        block_cursor.movePosition(QTextCursor.StartOfBlock)
                        block_cursor.insertText(" " * self.indent_size)
                    else:  # '<'
                        block_text = block.text()
                        leading_spaces = len(block_text) - len(block_text.lstrip(' '))
                        to_remove = min(leading_spaces, self.indent_size)
                        if to_remove > 0:
                            block_cursor.movePosition(QTextCursor.StartOfBlock)
                            block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, to_remove)
                            block_cursor.removeSelectedText()
            self.set_vim_state("NORMAL")
            cursor.clearSelection()
            self.setTextCursor(cursor)
            return
            
        self.setTextCursor(cursor)

    # Vim Operations
    def vim_delete_line(self, count=1):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        for _ in range(count):
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        if not cursor.hasSelection():
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.yank_buffer = cursor.selectedText()
        self.yank_is_line = True
        cursor.removeSelectedText()
        self.setTextCursor(cursor)

    def vim_delete_to_char(self, char, include_char=True, count=1):
        cursor = self.textCursor()
        current_line = cursor.block().text()
        pos = cursor.positionInBlock()
        idx = pos
        for _ in range(count):
            idx = current_line.find(char, idx + 1)
            if idx == -1:
                break
        if idx != -1:
            target_pos = cursor.block().position() + idx
            if include_char:
                target_pos += 1
            cursor.setPosition(target_pos, QTextCursor.KeepAnchor)
            self.yank_buffer = cursor.selectedText()
            self.yank_is_line = False
            cursor.removeSelectedText()
            self.setTextCursor(cursor)

    def vim_delete_word(self, count=1):
        cursor = self.textCursor()
        for _ in range(count):
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            while True:
                if not cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                    break
                char = cursor.selectedText()[-1:]
                if char != " ":
                    cursor.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
                    break
        self.yank_buffer = cursor.selectedText()
        self.yank_is_line = False
        cursor.removeSelectedText()
        self.setTextCursor(cursor)

    def vim_shift_left(self, count=1):
        cursor = self.textCursor()
        start_block = cursor.blockNumber()
        for i in range(count):
            block = self.document().findBlockByNumber(start_block + i)
            if not block.isValid():
                break
            text = block.text()
            leading_spaces = len(text) - len(text.lstrip(' '))
            spaces_to_remove = min(leading_spaces, self.indent_size)
            if spaces_to_remove > 0:
                block_cursor = QTextCursor(block)
                block_cursor.movePosition(QTextCursor.StartOfBlock)
                block_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, spaces_to_remove)
                block_cursor.removeSelectedText()

    def vim_shift_right(self, count=1):
        cursor = self.textCursor()
        start_block = cursor.blockNumber()
        for i in range(count):
            block = self.document().findBlockByNumber(start_block + i)
            if not block.isValid():
                break
            block_cursor = QTextCursor(block)
            block_cursor.movePosition(QTextCursor.StartOfBlock)
            block_cursor.insertText(" " * self.indent_size)

    def vim_change_case_lines(self, mode, count=1):
        cursor = self.textCursor()
        start_block = cursor.blockNumber()
        for i in range(count):
            block = self.document().findBlockByNumber(start_block + i)
            if not block.isValid():
                break
            block_cursor = QTextCursor(block)
            block_cursor.movePosition(QTextCursor.StartOfBlock)
            block_cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            text = block_cursor.selectedText()
            new_text = text.lower() if mode == 'gu' else text.upper()
            block_cursor.insertText(new_text)

    def vim_change_case_words(self, mode, count=1):
        cursor = self.textCursor()
        for _ in range(count):
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        new_text = text.lower() if mode == 'gu' else text.upper()
        cursor.insertText(new_text)
        self.setTextCursor(cursor)

    def vim_toggle_case(self, count=1):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, count)
        text = cursor.selectedText()
        toggled_chars = []
        for char in text:
            if char.islower():
                toggled_chars.append(char.upper())
            elif char.isupper():
                toggled_chars.append(char.lower())
            else:
                toggled_chars.append(char)
        toggled_text = "".join(toggled_chars)
        cursor.insertText(toggled_text)
        self.setTextCursor(cursor)

    def vim_paragraph_backward(self, count=1, keep_anchor=False):
        cursor = self.textCursor()
        move_anchor = QTextCursor.KeepAnchor if keep_anchor else QTextCursor.MoveAnchor
        for _ in range(count):
            cursor.movePosition(QTextCursor.Up, move_anchor)
            while cursor.block().text().strip() != "":
                if not cursor.movePosition(QTextCursor.Up, move_anchor):
                    break
        cursor.movePosition(QTextCursor.StartOfLine, move_anchor)
        self.setTextCursor(cursor)

    def vim_paragraph_forward(self, count=1, keep_anchor=False):
        cursor = self.textCursor()
        move_anchor = QTextCursor.KeepAnchor if keep_anchor else QTextCursor.MoveAnchor
        for _ in range(count):
            cursor.movePosition(QTextCursor.Down, move_anchor)
            while cursor.block().text().strip() != "":
                if not cursor.movePosition(QTextCursor.Down, move_anchor):
                    break
        cursor.movePosition(QTextCursor.StartOfLine, move_anchor)
        self.setTextCursor(cursor)

    def vim_sentence_backward(self, count=1, keep_anchor=False):
        cursor = self.textCursor()
        move_anchor = QTextCursor.KeepAnchor if keep_anchor else QTextCursor.MoveAnchor
        text = self.toPlainText()
        pos = cursor.position()
        for _ in range(count):
            start_idx = pos - 2
            j = pos - 1
            while j >= 0 and text[j] == ' ':
                j -= 1
            if j >= 0 and text[j] in ('.', '!', '?', '\n'):
                start_idx = j - 1
                
            found = False
            for i in range(start_idx, -1, -1):
                if i > 0 and text[i] == "\n" and text[i-1] == "\n":
                    pos = i + 1
                    found = True
                    break
                if text[i] in ('.', '!', '?') and i < len(text) - 1 and text[i+1] in (' ', '\n'):
                    pos = i + 1
                    while pos < len(text) - 1 and text[pos] == ' ':
                        pos += 1
                    found = True
                    break
            if not found:
                pos = 0
                break
        cursor.setPosition(pos, move_anchor)
        self.setTextCursor(cursor)

    def vim_sentence_forward(self, count=1, keep_anchor=False):
        cursor = self.textCursor()
        move_anchor = QTextCursor.KeepAnchor if keep_anchor else QTextCursor.MoveAnchor
        text = self.toPlainText()
        pos = cursor.position()
        for _ in range(count):
            found = False
            for i in range(pos + 1, len(text)):
                if i < len(text) - 1 and text[i] == "\n" and text[i+1] == "\n":
                    pos = i + 2
                    found = True
                    break
                if text[i] in ('.', '!', '?') and i < len(text) - 1 and text[i+1] in (' ', '\n'):
                    pos = i + 1
                    while pos < len(text) - 1 and text[pos] == ' ':
                        pos += 1
                    found = True
                    break
            if not found:
                pos = len(text)
                break
        cursor.setPosition(pos, move_anchor)
        self.setTextCursor(cursor)

    def vim_yank_line(self, count=1):
        original_cursor = self.textCursor()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        for _ in range(count):
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        if not cursor.hasSelection() or cursor.block().blockNumber() == self.document().blockCount() - 1:
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.yank_buffer = cursor.selectedText()
        if not self.yank_buffer.endswith("\n") and not self.yank_buffer.endswith("\u2029"):
            self.yank_buffer += "\n"
        self.yank_is_line = True
        self.setTextCursor(original_cursor)

    def vim_paste(self):
        if not self.yank_buffer:
            return
        cursor = self.textCursor()
        if self.yank_is_line:
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n" + self.yank_buffer.rstrip("\n"))
        else:
            cursor.insertText(self.yank_buffer)
        self.setTextCursor(cursor)

    def vim_find_char(self, char, count=1):
        cursor = self.textCursor()
        current_line = cursor.block().text()
        pos = cursor.positionInBlock()
        idx = pos
        for _ in range(count):
            idx = current_line.find(char, idx + 1)
            if idx == -1:
                break
        if idx != -1:
            cursor.setPosition(cursor.block().position() + idx)
            self.setTextCursor(cursor)

    # Line numbering helper methods
    def lineNumberAreaWidth(self):
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks /= 10
            digits += 1
        space = 5 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).y())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#808080"))
                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def setErrorLines(self, lines):
        ''' Set the 0-based block/line indices that should be highlighted as errors '''
        self.error_lines = set(lines)
        self.highlightCurrentLineAndErrors()

    def highlightCurrentLineAndErrors(self):
        extraSelections = []
        
        # Add highlight for current line
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#EAF2FB") # Subtle blue
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            
        # Add highlights for lines with errors
        doc = self.document()
        for line_num in self.error_lines:
            block = doc.findBlockByLineNumber(line_num)
            if block.isValid():
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor("#FFCCCC")) # Light red
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                cursor = QTextCursor(block)
                selection.cursor = cursor
                extraSelections.append(selection)
                
        self.setExtraSelections(extraSelections)


# LSP Client Classes and Helpers
class LSPSignalEmitter(QObject):
    diagnostics_received = Signal(list) # Emits lists of dicts: {"line": int, "message": str}


class LSPReader(threading.Thread):
    def __init__(self, stream, signal_emitter):
        super().__init__()
        self.stream = stream
        self.signal_emitter = signal_emitter
        self.daemon = True
        self.running = True

    def run(self):
        buffer = b""
        while self.running:
            try:
                chunk = self.stream.read(1024)
                if not chunk:
                    break
                buffer += chunk
                while b"\r\n\r\n" in buffer:
                    parts = buffer.split(b"\r\n\r\n", 1)
                    header_part = parts[0]
                    body_part = parts[1]
                    
                    content_length = None
                    for line in header_part.decode('utf-8', errors='replace').split("\r\n"):
                        if line.startswith("Content-Length:"):
                            content_length = int(line.split(":", 1)[1].strip())
                            break
                            
                    if content_length is None:
                        buffer = body_part
                        continue
                        
                    if len(body_part) >= content_length:
                        json_data = body_part[:content_length]
                        buffer = body_part[content_length:]
                        try:
                            msg = json.loads(json_data.decode('utf-8', errors='replace'))
                            if "method" in msg and msg["method"] == "textDocument/publishDiagnostics":
                                params = msg.get("params", {})
                                diagnostics = params.get("diagnostics", [])
                                errors = []
                                for diag in diagnostics:
                                    start = diag.get("range", {}).get("start", {})
                                    line = start.get("line", 0) # 0-based
                                    message = diag.get("message", "")
                                    errors.append({"line": line, "message": message})
                                self.signal_emitter.diagnostics_received.emit(errors)
                        except Exception as e:
                            print("LSP JSON parse error:", e)
                    else:
                        break
            except Exception as e:
                break


def send_lsp_message(stream, msg):
    try:
        content = json.dumps(msg).encode('utf-8')
        headers = f"Content-Length: {len(content)}\r\n\r\n".encode('utf-8')
        stream.write(headers + content)
        stream.flush()
    except Exception as e:
        print("LSP send error:", e)


class ASN1LSPClient:
    def __init__(self, server_path, current_file_path, signal_emitter):
        self.server_path = server_path
        self.current_file_path = os.path.abspath(current_file_path)
        self.signal_emitter = signal_emitter
        self.process = None
        self.reader = None
        self.lsp_version = 1

    def start(self):
        try:
            self.process = subprocess.Popen(
                [self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            self.reader = LSPReader(self.process.stdout, self.signal_emitter)
            self.reader.start()
            
            # Send initialize request
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "processId": os.getpid(),
                    "rootUri": "file://" + os.path.dirname(self.current_file_path),
                    "capabilities": {}
                }
            }
            send_lsp_message(self.process.stdin, init_req)
            
            # Send initialized notification
            init_notif = {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            }
            send_lsp_message(self.process.stdin, init_notif)
            
        except Exception as e:
            print("Failed to start LSP server:", e)

    def did_open(self, content):
        if not self.process:
            return
        open_notif = {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": "file://" + self.current_file_path,
                    "languageId": "asn1",
                    "version": self.lsp_version,
                    "text": content
                }
            }
        }
        send_lsp_message(self.process.stdin, open_notif)

    def did_change(self, content):
        if not self.process:
            return
        self.lsp_version += 1
        change_notif = {
            "jsonrpc": "2.0",
            "method": "textDocument/didChange",
            "params": {
                "textDocument": {
                    "uri": "file://" + self.current_file_path,
                    "version": self.lsp_version
                },
                "contentChanges": [
                    {
                        "text": content
                    }
                ]
            }
        }
        send_lsp_message(self.process.stdin, change_notif)

    def stop(self):
        if self.reader:
            self.reader.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
