#!/usr/bin/env python

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    This module is an easter egg.

    Credits:
    Rendering algorithm to transform graphviz b-splines to to Qt bezier curves
    was developed by Steve Dodier-Lazaro (www.mupuf.org)

    Contact: maxime.perrotin@esa.int
"""
import logging
import math
import random

from PySide import QtGui, QtCore
from PySide.QtCore import QPointF
from PySide.QtGui import QPainterPath

try:
    from PySide import phonon
except ImportError:
    # In some distributions, phonon cannot be installed properly
    # Discard - but sound will not work.
    pass
import genericSymbols
import icons

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Rocket(genericSymbols.Symbol, object):
    ''' An Opengeode rocket '''
    _unique_followers = []
    _insertable_followers = []
    _terminal_followers = []

    def __init__(self):
        ''' Initialization: compute the polygon shape '''
        super(Rocket, self).__init__(parent=None)
        self.set_shape(30, 60)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 202)))
        # Set the rotation origin point
        self.setTransformOriginPoint(self.boundingRect().center())

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QtGui.QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width / 3, height / 6)
        path.lineTo(width / 3, height - height / 6)
        path.lineTo(width - width / 3, height - height / 6)
        path.lineTo(width - width / 3, height / 6)
        path.lineTo(width / 2, 0)
        path.moveTo(width / 3, height / 2)
        path.lineTo(0, height / 2)
        path.lineTo(0, height)
        path.lineTo(width / 6, height - height / 6)
        path.lineTo(width / 3, height)
        path.lineTo(width / 3, height - height / 6)
        path.moveTo(width - width / 3, height / 2)
        path.lineTo(width, height / 2)
        path.lineTo(width, height)
        path.lineTo(width - width / 6, height - height / 6)
        path.lineTo(width - width / 3, height)
        path.lineTo(width - width / 3, height - height / 6)
        self.setPath(path)
        super(Rocket, self).set_shape(width, height)

    def _rotation(self):
        ''' Qt Property that can be used in animations '''
        return self.rotation()

    def _set_rotation(self, value):
        ''' Qt Property that can be used in animations '''
        self.setRotation(value)

    angle = QtCore.Property(float, _rotation, _set_rotation)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Rocket at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_move(self, event):
        ''' Discard mouse move '''
        pass

    def mouse_release(self, _):
        ''' Mouse has no effect on the rocket '''
        pass


class Lander(object):
    ''' Rocket Lander '''
    def __init__(self, scene):
        ''' Initialize the game '''
        self.scene = scene
        scene.scene_left.connect(self.quit_scene)
        self.rocket = Rocket()
        self.width = self.scene.sceneRect().width()
        self.height = self.scene.sceneRect().height()

        self.screen_bottom = self.height - self.rocket.boundingRect().height()
        scene.addItem(self.rocket)

        # Compute random land points
        random.seed()
        p1 = QPointF(0.0, random.uniform(0.0, self.height))
        p2 = QPointF(random.uniform(0.0, self.width / 4.0),
                    random.uniform(0.0, self.height))
        p3 = QPointF(random.uniform(p2.x(), 2 * self.width / 3.0), self.height)
        p4 = QPointF(p3.x() + 40.0, self.height)
        p5 = QPointF(self.width, random.uniform(0.0, self.height))
        path = QPainterPath(p1)
        slope = (p2.y() - p1.y()) / (p2.x() - p1.x())
        sign = 3
        for point in range(int((p2.x() - p1.x()) / 5)):
            sign = -sign
            x = p1.x() + point * 5
            path.lineTo(x, slope * x + sign)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p4)
        path.lineTo(p5)
        scene.addPath(path)

        # Initialize the music
        try:
            self.music = phonon.Phonon.createPlayer(
                    phonon.Phonon.MusicCategory,
                    phonon.Phonon.MediaSource(':/lander.mp3'))
        except NameError:
            LOG.warning('Could not initialise phonon')
        # Initialize the animation for the translation of the rocket
        self.animation = QtCore.QPropertyAnimation(self.rocket, "position")
        self.rocket_position = None
        # Initialize the animation for the rotation of the rocket
        self.rotation = QtCore.QPropertyAnimation(self.rocket, "angle")

        # Catch the key events to add user interaction:
        self.scene.keyPressEvent = lambda x: self.key(x)

        # updateCurrentTime is called by Qt when time changes
        self.animation.updateCurrentTime = lambda x: self.time_progress(x)
        # Connect signal sent at end of animation
        self.animation.finished.connect(self.animation_finished)

    def time_progress(self, time_value):
        ''' Called when time changes - used to estimate rocket speed '''
        # Call super function - it computes the new position
        super(QtCore.QPropertyAnimation,
                self.animation).updateCurrentTime(time_value)
        if self.rocket.pos().y() - self.rocket_position.y() > 0.1:
            self.rocket.speed = 'high'
        else:
            self.rocket.speed = 'low'
        self.rocket_position = self.rocket.pos()

    def key(self, evt):
        ''' Handling of key press event '''
        # Discard keys if there is a running rotation animation
        if self.rotation.state() != QtCore.QAbstractAnimation.Stopped:
            return
        self.rotation.setDuration(500)
        self.rotation.setStartValue(self.rocket.angle)
        self.rotation.setEasingCurve(QtCore.QEasingCurve.Linear)
        if evt.key() == QtCore.Qt.Key_Right:
            self.rotation.setEndValue(self.rocket.angle + 30.0)
            self.rotation.start()
        elif evt.key() == QtCore.Qt.Key_Left:
            self.rotation.setEndValue(self.rocket.angle - 30.0)
            self.rotation.start()
        elif evt.key() == QtCore.Qt.Key_Up:
            # Up key action depends on current speed and angle
            self.animation.stop()
            end_value = self.animation.endValue()
            remaining_time = (self.animation.totalDuration() -
                             self.animation.currentTime())
            if 90 < abs(self.rocket.angle) < 270:
                # If the rocket nose is towards Earth
                nose = 'down'
                delta_y = -(self.screen_bottom - self.rocket.y())
                hypo = delta_y / math.cos(math.radians(self.rocket.angle))
                delta_x = hypo * math.sin(math.radians(self.rocket.angle))
            else:
                nose = 'up'
                delta_x = 70.0 * math.sin(math.radians(self.rocket.angle))
                delta_y = 70.0 * math.cos(math.radians(-self.rocket.angle))
            if(nose == 'up' and end_value.y() > self.rocket.y() and
                    self.rocket.speed == 'high'):
                # Delay impact time by 2 seconds if going down at high speed
                self.animation.setDuration(remaining_time + 2000)
                self.animation.setStartValue(self.rocket.pos())
                self.animation.start()
                return
            elif end_value.y() > self.rocket.y() and (
                    self.rocket.speed == 'low' or nose == 'down'):
                end_value.setX(self.rocket.x() + delta_x)
                end_value.setY(self.rocket.y() - delta_y)
            else:
                end_value.setX(end_value.x() + delta_x)
                end_value.setY(end_value.y() - delta_y)
            self.animation.setDuration(2000)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutExpo)
            self.animation.setStartValue(self.rocket.pos())
            self.animation.setEndValue(end_value)
            self.animation.start()

        elif evt.key() == QtCore.Qt.Key_Down:
            # Down key has no effect
            pass
        else:
            pass

    def play(self):
        ''' Run the game '''
        self.rocket.setPos(0, 0)
        try:
            self.music.play()
        except AttributeError:
            pass
        self.animation.setDuration(20000)
        self.animation.setStartValue(self.rocket.pos())
        # Store initial position - used to compute rocket speed
        self.rocket_position = self.rocket.pos()
        self.animation.setEndValue(QtCore.QPointF(350, self.screen_bottom))
        self.animation.setEasingCurve(QtCore.QEasingCurve.InCirc)
        self.animation.start()

    def animation_finished(self):
        ''' When animation is finished, check if another one is needed '''
        if self.rocket.y() < self.screen_bottom:
            end_value = self.animation.endValue()
            end_value.setY(self.screen_bottom)
            self.animation.setStartValue(self.rocket.pos())
            self.animation.setEndValue(end_value)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InCirc)
            self.animation.setDuration(abs(self.rocket.y()) * 500)
            self.animation.start()
        else:
            print 'GAME OVER'

    def quit_scene(self):
        ''' Redefinition of the quit_scene: Stop the game and the music '''
        try:
            self.music.stop()
        except AttributeError:
            pass


if __name__ == '__main__':
    print('What do you expect?')
