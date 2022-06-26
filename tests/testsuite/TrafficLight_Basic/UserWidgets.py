#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' Edit this module at will to create custom widgets that can send TC or
    receive TM - and do anything you like with the data.
    (c) 2016-2019 European Space Agency
'''

__author__ = "Maxime Perrotin, Thanassis Tsiodras"
__license__ = "LGPL"
__url__ = "https://taste.tools"

import sys
import os
import importlib
import DV
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from asn1_value_editor import UserWidgetsCommon

# ** IMPORTANT **
# you must list here the classes you want to expose to the GUI:
__all__ = ['PedestrianButton', 'TrafficLight', 'Pedestrian']


class PedestrianButton(UserWidgetsCommon.TC):
    ''' Fill / mimic this class to create a custom TC widget '''
    name = 'Nice Button' # name on the GUI combo button
    instantiated = False

    def __init__(self, asn1_typename, parent):
        ''' Initialise the widget '''
        super(PedestrianButton, self).__init__(asn1_typename, parent)

        if PedestrianButton.instantiated:
            self.close()
            return

        self._asn1_typename = asn1_typename

        self.widget = QPushButton("Request passage")
        self.widget.clicked.connect(self.clicked)
        self.setWidget(self.widget)

        # parent is the ASN.1 value editor
        self.parent = parent
        self.setWindowTitle(parent.messageName)
        self.show()
        PedestrianButton.instantiated = True

    @staticmethod
    def applicable():
        ''' Return True to activate this widget '''
        return True

    @staticmethod
    def editorIsApplicable(editor):
        ''' Return true if this particular editor is compatible with this
        widget'''
        return editor.messageName == "Button"

    def clicked(self):
        ''' Called when user clicks on the button '''
        self.parent.sendTC()


class TrafficLight(UserWidgetsCommon.TM):
    '''Save telemetries in the database'''
    name = 'View Traffic Light'  # name for the combo button in the GUI

    def __init__(self, parent=None):
        ''' Initialise the widget '''
        super(TrafficLight, self).__init__(parent)
        self.widget = QLabel()
        self.colorMap = { DV.red: QPixmap ("red.png"),
                          DV.orange: QPixmap ("orange.png"),
                          DV.green: QPixmap ("green.png") }
        self.widget.setPixmap (self.colorMap[DV.red])
        self.setWidget(self.widget)
        self.setWindowTitle(parent.treeItem.text())
        self.show()

    @Slot()
    def new_tm(self):
        ''' Slot called when a TM has been received in the editor '''
        # Nothing to do, the update() function does nothing thread-related
        # that would need to be done here
        pass

    def update(self, value):
        ''' Receive ASN.1 value '''
        color = value.Get()
        self.widget.setPixmap (self.colorMap[color])

    @staticmethod
    def applicable():
        ''' Return True to enable this widget '''
        return True

    @staticmethod
    def editorIsApplicable(editor):
        ''' Return true if this particular editor is compatible with this
        widget'''
        return editor.messageName == "Color"

class Pedestrian(UserWidgetsCommon.TM):
    '''Save telemetries in the database'''
    name = 'View Traffic Light'  # name for the combo button in the GUI

    def __init__(self, parent=None):
        ''' Initialise the widget '''
        super(Pedestrian, self).__init__(parent)
        self.widget = QLabel()
        self.colorMap = { DV.wait: QPixmap ("wait.png"),
                          DV.go: QPixmap ("go.png")}
        self.widget.setPixmap (self.colorMap[DV.wait])
        self.setWidget(self.widget)
        self.setWindowTitle(parent.treeItem.text())
        self.show()

    @Slot()
    def new_tm(self):
        ''' Slot called when a TM has been received in the editor '''
        # Nothing to do, the update() function does nothing thread-related
        # that would need to be done here
        pass

    def update(self, value):
        ''' Receive ASN.1 value '''
        status = value.Get()
        self.widget.setPixmap (self.colorMap[status])

    @staticmethod
    def applicable():
        ''' Return True to enable this widget '''
        return True

    @staticmethod
    def editorIsApplicable(editor):
        ''' Return true if this particular editor is compatible with this
        widget'''
        return editor.messageName == "Info_User"

if __name__ == '__main__':
    print('This module can only be imported from the main TASTE guis')
    sys.exit(-1)
