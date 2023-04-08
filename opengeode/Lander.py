#!/usr/bin/env python3

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    This module is an easter egg, inspired by an old DOS basic game (LANDER.BAS).

    Contact: maxime.perrotin@esa.int
"""
import logging
import math
import random

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader

try:
    from PySide6.QtMultimedia import *
except ImportError:
    pass

from . import genericSymbols, icons

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Rocket(genericSymbols.Symbol, object):
    ''' An Opengeode rocket '''
    _unique_followers = []
    _insertable_followers = []
    _terminal_followers = []

    def __init__(self):
        ''' Initialization: compute the polygon shape '''
        super().__init__(parent=None)
        self.set_shape(30, 40)
        self.setBrush(QBrush(QColor(255, 255, 255)))
        # Set the rotation origin point
        self.setTransformOriginPoint(self.boundingRect().center())

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width / 3, height / 6)
        path.lineTo(width / 3, height - height / 6)
        path.lineTo(width - width / 3, height - height / 6)
        path.lineTo(width - width / 3, height / 6)
        path.lineTo(width / 2, 0)

        # left booster
        path.moveTo(width / 3, height / 2)
        path.lineTo(width / 6, height / 2)
        path.lineTo(width / 6, height)
        path.lineTo(width / 4, height - height / 6)
        path.lineTo(width / 3, height)
        path.lineTo(width / 3, height - height / 6)
        # right booster
        path.moveTo(width - width / 3, height / 2)
        path.lineTo(width-(width/6), height / 2)
        path.lineTo(width-(width/6), height)
        path.lineTo(width - width / 4, height - height / 6)
        path.lineTo(width - width / 3, height)
        path.lineTo(width - width / 3, height - height / 6)
        self.setPath(path)
        super().set_shape(width, height)

    def _rotation(self):
        ''' Qt Property that can be used in animations '''
        return self.rotation()

    def _set_rotation(self, value):
        ''' Qt Property that can be used in animations '''
        if value == 360:
            value = 0
        self.setRotation(value)

    angle = Property(float, _rotation, _set_rotation)

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


class Lander:
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

        # Compute random land field
        lp = 150
        lx = [0] * lp
        ly = [0] * lp
        lax = [0] * lp
        lay = [0] * lp
        lx[0] = 0
        ly[0] = 40
        for i in range (1, lp):
            lx[i] = i * self.width / lp

        random.seed()
        p1 = QPointF(0, 0)
        path = QPainterPath(p1)
        # Define coordinates of the landing area
        bot = self.width * random.uniform(0, 1)
        for i in range(1, lp):
            # Determine the angle between the current x-coordinate and the landing field
            angle = math.pi * (lx[i] - bot - 15) / (self.width * 1.5)
            # Determine the y-coordinate based on the cosine of the angle
            ly[i] = ly[0] + (self.height - ly[0]) * abs(math.cos(angle))
            # Add some random noise to the y-coordinate to make the land contour look more realistic
            ly[i] += math.sqrt(ly[i]) * (0.5 - random.uniform(0, 1))
            # If the point falls within the landing field, set its y-coordinate to the height of the landing field
            if bot < lx[i] < bot + 30:
                ly[i] = self.height - 2
            # Prevent overflow of the screen
            if ly[i] > self.height - 2:
                ly[i] = self.height - 2
            # Draw a line segment connecting the current point to the previous point
            path.lineTo(lx[i], ly[i])
        path.lineTo(lx[i], self.height)
        path.lineTo(0, self.height)
        path.lineTo(0,0)
        brush = QBrush(QColor(246, 241, 213))
        self.landscape = scene.addPath(path, brush=brush)

        # Define parameters used to control the physics
        self.thrust = 10
        self.tilt = 0  # used to index "ang" hich is the angle in degree
        self.speed_x = 30
        self.speed_y = 0
        self.x = 0
        self.y = 0
        self.gravity = 10
        self.fuel = 4000
        # these are the possible angles (0 = vertical)
        # the arrows allow to go from one to the next
        self.ang = [0, 15, 30, 45, 60, 90, 180, 270, 285, 300, 315, 330, 345]
        self.nang = len(self.ang)    # number of angles

        # landing pad
        brush = QBrush(QColor(228, 48, 32)) # red from Tintin's rocket
        path=QPainterPath()
        x1, y1 = bot, self.height - 15
        x2, y2 = bot + 30, self.height
        path.addRect(x1, y1, x2-x1, y2-y1)
        self.pad = scene.addPath(path, brush=brush)

        # Initialize the music
        try:
            self.music = QMediaPlayer()
            audioOutput = QAudioOutput()
            self.music.setAudioOutput(audioOutput)
            self.music.setSource(QUrl.fromLocalFile('lander.mp3'))
        except NameError:
            LOG.warning('Could not initialise QtMultimedia')
        # Initialize the animation for the translation of the rocket
        self.animation = QPropertyAnimation(self.rocket, b"position")
        # Initialize the animation for the rotation of the rocket
        self.rotation = QPropertyAnimation(self.rocket, b"angle")

        # Catch the key events to add user interaction:
        self.scene.keyPressEvent = lambda x: self.key(x)

        # updateCurrentTime is called by Qt when time changes
        self.animation.updateCurrentTime = lambda x: self.time_progress(x)
        # Connect signal sent at end of animation
        self.animation.finished.connect(self.animation_finished)

    def time_progress(self, time_value):
        ''' Called when time changes - not used '''
        # Call super function - it computes the new position
        super(QPropertyAnimation,
                self.animation).updateCurrentTime(time_value)

    def key(self, evt):
        ''' Handling of key press event '''
        # Discard keys if there is a running rotation animation
        if self.rotation.state() != QAbstractAnimation.Stopped:
            return
        self.rotation.setDuration(200)
        self.rotation.setEasingCurve(QEasingCurve.Linear)
        if evt.key() == Qt.Key_Right:
            self.tilt = self.tilt + 1 if self.tilt < self.nang - 1 else 0
            end_value = self.ang[self.tilt] if self.tilt != 0 else 360
            self.rotation.setStartValue(self.rocket.angle)
            self.rotation.setEndValue(end_value)
            self.rotation.start()
        elif evt.key() == Qt.Key_Left:
            if self.tilt == 0:
                self.rocket.setRotation(360)
                self.tilt = self.nang - 1
            else:
                self.tilt -= 1
            end_value = self.ang[self.tilt]
            self.rotation.setStartValue(self.rocket.angle)
            self.rotation.setEndValue(end_value)
            self.rotation.start()
        elif evt.key() == Qt.Key_Up:
            self.thrust = self.thrust + 1 if self.thrust < 19 else 19
        elif evt.key() == Qt.Key_Down:
            # Reduce thrust
            self.thrust = self.thrust - 1 if self.thrust > 0 else 0
        else:
            pass

    def play(self):
        ''' Run the game '''
        self.rocket.setPos(self.x, self.y)
        try:
            self.music.play()
        except AttributeError:
            pass
        self.animation.setDuration(200)
        self.animation.setStartValue(self.rocket.pos())
        self.update_control()   # compute next position
        self.animation.setEndValue(QPointF(self.x, self.y))
        self.animation.setEasingCurve(QEasingCurve.InCirc)
        self.animation.start()

    def update_control(self):
        ''' Compute position and speed based on thrust and tilt '''
        # Update control
        self.speed_y += self.gravity - self.thrust * math.cos(math.pi * self.ang[self.tilt] / 180)
        self.speed_x = 0.9 * self.speed_x + self.thrust * math.sin(math.pi * self.ang[self.tilt] / 180)
        if self.speed_y < -10:
            self.speed_y = -10
        self.x += self.speed_x * 0.05
        self.y += self.speed_y * 0.05
        if self.y < 0:
            self.y = 0
        self.fuel = self.fuel - self.thrust
        if self.fuel < 0:
            self.fuel = 0

    def animation_finished(self):
        ''' When animation is finished, check if another one is needed '''
        for item in self.rocket.collidingItems():
            if item == self.landscape:
                print("CRASH - GAME OVER")
                return
            elif item == self.pad:
                if self.speed_y < 100:
                    print ("CONGRATULATIONS")
                else:
                    print ("TOO FAST ! GAME OVER")
                    print (self.speed_y)
                return
        if self.rocket.y() < self.screen_bottom:
            self.update_control()
            self.animation.setEndValue(QPointF(self.x, self.y))
            self.animation.setStartValue(self.rocket.pos())
            self.animation.setEasingCurve(QEasingCurve.InCirc)
            self.animation.setDuration(200)
            self.animation.start()
        else:
            print('GAME OVER')

    def quit_scene(self):
        ''' Redefinition of the quit_scene: Stop the game and the music '''
        try:
            self.music.stop()
        except AttributeError:
            pass


if __name__ == '__main__':
    print('What do you expect?')
