#!/usr/bin/env python3
"""
    OpenGEODE - TASTE SDL and Observers Editor

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2022 Maxime Perrotin & European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int


    This module handles the Opengeode Help tab
    The content of the help is extracted from the TASTE wiki using
    the exportedMediaWiki2HTML application.
    To extract the "SDL Tutorial page" the following command is invoked:
    exportMediaWiki2Html.py -l http://taste.tuxfamily.org/wiki/ -g 357
"""
from PySide6.QtWidgets import *
from PySide6.QtHelp import *
from PySide6.QtCore import *
from . import icons

import time


class OG_HelpEngine(QHelpEngine):
    def __init__(self):
        ''' Load the help file '''
        # QHelp does not work with Qt resources so we must first
        # dump the files to disk...
        for f in ('opengeode.qhc', 'opengeode.qch'):
            qrc = QFile(f':help/{f}')
            qrc.open(QIODevice.ReadOnly)
            content = qrc.readAll()
            helpfile = f'/tmp/{f}'
            with open(helpfile, 'wb') as tmpfile:
                tmpfile.write(content.data())
        super().__init__('/tmp/opengeode.qhc')
        if not self.setupData():
            print("QHelp error:", self.error())

class OG_HelpBrowser(QTextBrowser):
    def __init__(self, parent=None):
        ''' The text browser is initialized with the application '''
        super().__init__(parent)
        self.engine = OG_HelpEngine();
        self.showHelpforKeyword("index")

    def showHelpforKeyword(self, idx):
        if self.engine:
            docs = self.engine.documentsForIdentifier(idx)
            if docs:
                self.setSource(docs[0].url)

    def loadResource(self, typ, url):
        ''' Re-implemented function. Called automatically by Qt '''
        if typ < 4 and self.engine:
            if url.isRelative():
                url=self.source().resolved(url)
            return self.engine.fileData(url)
