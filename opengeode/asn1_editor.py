# -*- coding: utf-8 -*-

"""
    OpenGEODE - ASN.1 File Editor extension
    Provides syntax highlighting, line numbers, autocompletion, and LSP diagnostics for ASN.1 files.
"""

import os
import json
import subprocess
import threading
from PySide6.QtWidgets import QPlainTextEdit, QCompleter, QWidget, QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor, QKeyEvent, QPainter, QTextFormat
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


class ASN1TextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer = None
        self.error_lines = set()
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

    def keyPressEvent(self, e: QKeyEvent):
        if self._completer and self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        # Insert 4 spaces on Tab instead of a literal tab character
        if e.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) and e.key() == Qt.Key_E)
        if not self._completer or not isShortcut:
            super().keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if not self._completer or (ctrlOrShift and e.text() == ""):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or e.text() == "" or len(completionPrefix) < 2 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)

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
