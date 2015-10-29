#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Diagram elements for connectors. Different types of connectors are
    available by default, such as lines, arrows, and bezier curves.

    The "Connection" class is the mother class, all other connectors must
    inherit from it and possibly redefine some functions or shape.

    Copyright (c) 2012-2014 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import math
import logging

from PySide.QtCore import Qt, QPointF, QLineF, Slot

from PySide.QtGui import(QGraphicsPathItem, QPainterPath, QGraphicsItem, QPen,
                         QPainter, QFont, QGraphicsTextItem, QColor,
                         QFontMetrics, QTextBlockFormat, QTextCursor)

import ogParser
from TextInteraction import EditableText

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Connection(QGraphicsPathItem, object):
    ''' Connection between two symbols (top-level class) '''
    # Default connections are not selectable
    default_cursor = Qt.ArrowCursor
    hasParent = False

    def __init__(self, parent, child):
        ''' Create a new connection between a parent and a child item '''
        super(Connection, self).__init__(parent)
        self.parent = parent
        self.child = child
        self._start_point = None
        self._end_point = None
        self._middle_points = []
        pen = QPen()
        pen.setColor(Qt.blue)
        pen.setCosmetic(False)
        self.setPen(pen)
        self.parent_rect = parent.sceneBoundingRect()
        self.childRect = child.sceneBoundingRect()
        # Activate cache mode to boost rendering by calling paint less often
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    @property
    def start_point(self):
        ''' Compute connection origin - redefine in subclasses '''
        return self._start_point or QPointF(0, 0)

    @property
    def end_point(self):
        ''' Compute connection end point - redefine in subclasses '''
        return self._end_point or QPointF(0, 0)

    @property
    def middle_points(self):
        ''' Compute connection intermediate points - redefine in subclasses '''
        return self._middle_points

    def top_level(self):
        ''' In case the connection has a text, implement top_level()
            as needed by TextInteraction '''
        return self.parent

    def simple_arrow(self, origin='head', path=None):
        ''' Compute the two points of an vertical arrow head '''
        if origin == 'head':
            endp = self.end_point
        else:
            endp = self.start_point
        return (QPointF(endp.x() - 5, endp.y() - 5),
                QPointF(endp.x() + 5, endp.y() - 5))

    def angle_arrow(self, path, origin='head'):
        ''' Compute the two points of the arrow head with the right angle '''
        if origin == 'tail':
            path = path.toReversed()
        length = path.length()
        percent = path.percentAtLength(length - 10.0)
        src = path.pointAtPercent(percent)
        #path.moveTo(path.pointAtPercent(1))
        end_point = path.pointAtPercent(1)
        #end_point = path.currentPosition()
        line = QLineF(src, end_point)
        angle = math.acos(line.dx() / (line.length() or 1))
        if line.dy() >= 0:
            angle = math.pi * 2 - angle
        arrow_size = 10.0
        arrow_p1 = end_point + QPointF(
                math.sin(angle - math.pi / 3) * arrow_size,
                math.cos(angle - math.pi / 3) * arrow_size)
        arrow_p2 = end_point + QPointF(
                math.sin(angle - math.pi + math.pi / 3) * arrow_size,
                math.cos(angle - math.pi + math.pi / 3) * arrow_size)
        return (arrow_p1, arrow_p2)

    def draw_arrow_head(self, shape, origin='head', kind='simple'):
        ''' Generic function to draw a simple arrow '''
        if kind == 'simple':
            arrowhead = self.simple_arrow(path=shape)
        else:
            arrowhead = self.angle_arrow(shape, origin)
        shape.lineTo(arrowhead[0])
        shape.moveTo(self.end_point if origin == 'head' else self.start_point)
        shape.lineTo(arrowhead[1])

    def __str__(self):
        ''' Print connection information for debug purpose'''
        return 'Connection: parent = {p}, child = {c}'.format(
                p=str(self.parentItem()), c=str(self.child))

    def reshape(self):
        ''' Update the connection or arrow shape '''
        shape = QPainterPath()
        shape.moveTo(self.start_point)
        for point in self.middle_points:
            shape.lineTo(point)
        shape.lineTo(self.end_point)
        # If required draw an arrow head (e.g. in SDL NEXTSTATE and JOIN)
        if self.child.arrow_head:
            self.draw_arrow_head(shape, origin='head',
                                 kind=self.child.arrow_head)
        if self.child.arrow_tail:
            shape.moveTo(shape.pointAtPercent(0))
            self.draw_arrow_head(shape, origin='tail',
                                 kind=self.child.arrow_head)
        self.setPath(shape)


class RakeConnection(Connection):
    ''' Fork-like connection, e.g. between a state and an input symbol '''
    @property
    def start_point(self):
        ''' Compute connection origin - redefined function '''
        parent_rect = self.parentItem().boundingRect()
        return QPointF(parent_rect.width() / 2, parent_rect.height())

    @property
    def end_point(self):
        ''' Compute connection end point - redefined function '''
        coord = self.child.pos()
        coord.setX(coord.x() + self.child.boundingRect().width() / 2)
        return coord

    @property
    def middle_points(self):
        ''' Compute connection intermediate points - redefined function '''
        yield QPointF(self.start_point.x(), self.start_point.y() + 10)
        yield QPointF(self.end_point.x(), self.start_point.y() + 10)


class JoinConnection(Connection):
    ''' Inverted fork-like connection, to join to a common point '''
    def reshape(self):
        ''' Update the connection shape - redefined: if the last element
        of a branch is e.g. a nextstate, don't join the connection point '''
        if self.parentItem().terminal_symbol:
            self.setPath(QPainterPath())
        else:
            super(JoinConnection, self).reshape()

    @property
    def start_point(self):
        ''' Compute connection origin - redefined function '''
        parent_rect = self.parentItem().boundingRect()
        return getattr(self.parentItem(), 'connectionPoint',
                       QPointF(parent_rect.width() / 2, parent_rect.height()))

    @property
    def end_point(self):
        ''' Compute connection end point - redefined function '''
        point_scene = self.child.mapToScene(self.child.connectionPoint)
        return self.mapFromScene(point_scene)

    @property
    def middle_points(self):
        ''' Compute connection intermediate points - redefined function '''
        yield QPointF(self.start_point.x(), self.end_point.y() - 10)
        yield QPointF(self.end_point.x(), self.end_point.y() - 10)


class VerticalConnection(Connection):
    ''' Vertical line with or without arrow '''
    @property
    def start_point(self):
        ''' Compute connection origin - redefined function '''
        parent_rect = self.parentItem().boundingRect()
        return getattr(self.parentItem(), 'connectionPoint',
                       QPointF(parent_rect.width() / 2, parent_rect.height()))

    @property
    def end_point(self):
        ''' Compute connection end point - redefined function '''
        point = self.child.pos()
        point.setX(self.start_point.x())
        return point


class CommentConnection(Connection):
    ''' Class handling connection to comment symbols, fixed at the right
        of a symbol '''
    @property
    def start_point(self):
        ''' Compute connection origin - redefined function '''
        parent_rect = self.parentItem().boundingRect()
        return QPointF(parent_rect.width(), parent_rect.height() / 2)

    @property
    def end_point(self):
        ''' Compute connection end point - redefined function '''
        if self.child.on_the_right:
            return QPointF(self.child.x(),
                   self.child.y() + self.child.boundingRect().height() / 2)
        else:
            return QPointF(self.child.x() + self.child.boundingRect().width(),
                   self.child.y() + self.child.boundingRect().height() / 2)

    @property
    def middle_points(self):
        ''' Compute connection intermediate points - redefined function '''
        # Make sure the connection does not overlap the comment item
        if (self.child.on_the_right or
               (not self.child.on_the_right and
               self.child.x() + self.child.boundingRect().width()
               < self.parentItem().boundingRect().width())):
            go_to_point = self.start_point.x() + 5
        else:
            go_to_point = self.end_point.x() + 5
        yield QPointF(go_to_point, self.start_point.y())
        yield QPointF(go_to_point, self.end_point.y())


class SignalList(EditableText):
    ''' Simplified text editor for signal lists '''
    def __init__(self, parent, text='', hyperlink = None):
        ''' Smaller font than normal text '''
        super(SignalList, self).__init__(parent, text)
        self.setFont(QFont('Ubuntu', pointSize=8))

    def set_text_alignment(self):
        ''' Text justification - ignore '''
        pass

    def set_textbox_position(self):
        ''' Alignment vs parent - ignore, done by the parent '''
        pass

    def try_resize(self):
        ''' Resizing of the parent when size expands - ignore '''
        pass

    # pylint: disable=C0103
    def focusOutEvent(self, event):
        ''' Redefined function - update in_sig and out_sig in parent '''
        super(SignalList, self).focusOutEvent(event)


class Signalroute(Connection):
    ''' Subclass of Connection used to draw channels between processes '''
    in_sig = out_sig = None
    completion_list = set()

    def __init__(self, process):
        ''' Set generic parameters from Connection class '''
        super(Signalroute, self).__init__(process, process)
        self.parser = ogParser
        self.blackbold = ()
        self.redbold = ()
        self.label_in = SignalList(parent=self)
        self.label_out = SignalList(parent=self)
        if not Signalroute.in_sig:
            # keep at class level as long as only one process is supported
            # when copy-pasting a process the challel in/out signal lists
            # are not parsed. Workaround is to keep the list "global"
            # to allow a copy of both process and channel
            # Needed for the image exporter, that copies the scene to a
            # temporary one
            Signalroute.in_sig = '{}'.format(',\n'.join(sig['name']
                                   for sig in process.input_signals))
            Signalroute.out_sig = '{}'.format(',\n'.join(sig['name']
                                    for sig in process.output_signals))
        self.label_in.setPlainText('[{}]'.format(self.in_sig))
        self.label_out.setPlainText('[{}]'.format(self.out_sig))
        self.label_in.document().contentsChanged.connect(self.change_siglist)
        self.label_out.document().contentsChanged.connect(self.change_siglist)
        for each in (self.label_in, self.label_out):
            each.show()
        self.process = process
        self.reshape()

    @Slot()
    def change_siglist(self):
        ''' Called when user modified the text of label_in or label_out '''
        for each in self.label_in, self.label_out:
            if not each.hasFocus():
                if not unicode(each).startswith('['):
                    each.setPlainText('[{}'.format(unicode(each)))
                if not unicode(each).endswith(']'):
                    each.setPlainText('{}]'.format(unicode(each)))
        Signalroute.in_sig = unicode(self.label_in)[1:-1]
        Signalroute.out_sig = unicode(self.label_out)[1:-1]


    @property
    def start_point(self):
        ''' Compute connection origin - redefined function '''
        parent_rect = self.process.boundingRect()
        return QPointF(parent_rect.x(), parent_rect.height() / 2)

    @property
    def end_point(self):
        ''' Compute connection end point - redefined function '''
        # Arrow always bumps at the screen edge
        try:
            view = self.scene().views()[0]
            view_pos = view.mapToScene(
                           view.viewport().geometry()).boundingRect().topLeft()
            scene_pos_x = self.mapFromScene(view_pos).x()
            return QPointF(scene_pos_x, self.start_point.y())
        except (IndexError, AttributeError):
            # In case there is no view (e.g. Export PNG from cmd line)
            return QPointF(self.start_point.x() - 250, self.start_point.y())

    def reshape(self):
        ''' Redefine shape function to add the text areas '''
        super(Signalroute, self).reshape()

        width_in = self.label_in.boundingRect().width()

        self.label_in.setX(self.start_point.x() - width_in)
        self.label_in.setY(self.start_point.y() + 5)
        self.label_out.setX(self.end_point.x() + 10)
        self.label_out.setY(self.end_point.y() + 5)

    def check_syntax(self, text):
        ''' Check the syntax of the IN and OUT signal lists '''
        try:
            _, syntax_errors, _, _, _ = self.parser.parseSingleElement(
                                           'signalroute', text)
        except (AssertionError, AttributeError) as err:
            LOG.error('Checker failed:' + str(err))
        else:
            return syntax_errors

    def update_completion_list(self, pr_text):
        ''' Called after text has been edited '''
        # TODO - call parseSingleElement, check sdlSymbols for examples
        pass

    def resize_item(self, new_rect):
        ''' Called after signallist text has been edited '''
        pass


class Controlpoint(QGraphicsPathItem, object):
    ''' Class handling one edge control point (to change bezier curves) '''
    def __init__(self, pos, edge):
        ''' Set the original control point - with color, shape '''
        path = QPainterPath()
        path.addEllipse(pos.x() - 5, pos.y() - 5, 10, 10)
        super(Controlpoint, self).__init__(path, parent=edge)
        self.setPen(QColor(50, 100, 120, 200))
        self.setBrush(QColor(200, 200, 210, 120))
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)
        self.edge = edge
        self.hide()

    @property
    def center(self):
        ''' Return the position of the center of the shape '''
        return self.pos() + self.boundingRect().center()

    def mouseMoveEvent(self, event):
        ''' When user moves a control point, update the connection shape '''
        super(Controlpoint, self).mouseMoveEvent(event)
        self.edge.reshape()


class Connectionpoint(Controlpoint):
    '''
        Class handling an end connection point - similar to Controlpoint,
        except the shape and the behaviour when moved. Connection point
        must check with its owning symbol if the move is valid.
    '''
    def __init__(self, pos, edge, symbol):
        ''' Create the point - as a small, lightblue box '''
        super(Connectionpoint, self).__init__(pos, edge=edge)
        path = QPainterPath()
        path.addRect(0, 0, 10, 10)
        self.setPath(path)
        self.setPos(pos.x() - 5, pos.y() - 5)
        # Symbol actually owning the connection point
        self.symbol = symbol

    def update_position(self):
        '''
            Update the position of the end point so that it is always
            placed correctly on the symbol that contains it (but that may
            not be the parent of the point if is the end point)
            After the position update, reshape the edge so that the lines
            are properly drawn to the new position
        '''
        # Transform position to owning symbol coordinates:
        center_pos = self.scenePos() + self.boundingRect().center()
        pos_symb = self.symbol.mapFromScene(center_pos)

        # Ask to symbol the nearest valid position on its shape
        # to place the connection point, and adjust position
        nearest_x, nearest_y = self.symbol.closest_connection_point(pos_symb)

        self.moveBy(-nearest_x, -nearest_y)

        self.edge.reshape()

    def mouseMoveEvent(self, event):
        '''
            When user moves the point, check with the connected symbol
            where the actual connection point should be placed
        '''
        # calling super function moves to the new point
        super(Connectionpoint, self).mouseMoveEvent(event)
        # Then compute a valid position, based on the owning symbol
        self.update_position()


class Edge(Connection):
    ''' B-spline/Bezier connection shape '''
    def __init__(self, edge, graph):
        ''' Set generic parameters from Connection class '''
        self.text_label = None
        super(Edge, self).__init__(edge['source'], edge['target'])
        self.edge = edge
        self.graph = graph
        # Set connection points as not visible, by default
        self.bezier_visible = False

        # Initialize control point coordinates
        self.bezier = [self.mapFromScene(*self.edge['spline'][0])]
        # Bezier control points (groups of three points):
        assert(len(self.edge['spline']) % 3 == 1)
        for i in xrange(1, len(self.edge['spline']), 3):
            self.bezier.append([Controlpoint(
                          self.mapFromScene(*self.edge['spline'][i + j]), self)
                          for j in range(3)])

        # Create connection points at start and end of the edge
        self.source_connection = Connectionpoint(
                self.start_point or self.bezier[0], self, self.parent)
        self.parent.movable_points.append(self.source_connection)
        self.end_connection = Connectionpoint(
                self.end_point or self.bezier[-1], self, self.child)
        self.child.movable_points.append(self.end_connection)
        self.reshape()

    @property
    def start_point(self):
        ''' Compute connection origin - redefine in subclasses '''
        # Start point is optional - graphviz decision
        return self.mapFromScene(*self.edge['start']) \
               if self.edge.get('start') else None

    @property
    def end_point(self):
        ''' Compute connection end point - redefine in subclasses '''
        return self.mapFromScene(*self.edge['end']) \
               if self.edge.get('end') else None

    def bezier_set_visible(self, visible=True):
        ''' Display or hide the edge control points '''
        self.bezier_visible = visible
        for group in self.bezier[1:]:
            for ctrl_point in group:
                if visible:
                    ctrl_point.show()
                else:
                    ctrl_point.hide()
        if visible:
            self.end_connection.show()
            self.source_connection.show()
        else:
            self.end_connection.hide()
            self.source_connection.hide()
        self.update()

    def mousePressEvent(self, event):
        ''' On a mouse click, display the control points '''
        self.bezier_set_visible(True)

    # pylint: disable=R0914
    def reshape(self):
        ''' Update the shape of the edge (redefined function) '''
        path = QPainterPath()
        # If there is a starting point, draw a line to the first curve point
        if self.start_point:
            path.moveTo(self.source_connection.center)
            path.lineTo(self.bezier[0])
        else:
            path.moveTo(self.source_connection.center)
        # Loop over the curve points:
        for group in self.bezier[1:]:
            path.cubicTo(*[point.center for point in group])

        # If there is an ending point, draw a line to it
        if self.end_point:
            path.lineTo(self.end_connection.center)

        end_point = path.currentPosition()
        arrowhead = self.angle_arrow(path)
        path.lineTo(arrowhead[0])
        path.moveTo(end_point)
        path.lineTo(arrowhead[1])
        path.moveTo(end_point)
        try:
            # Add the transition label, if any (none for the START edge)
            font = QFont('arial', pointSize=8)
            metrics = QFontMetrics(font)
            label = self.edge.get('label', '') or ''
            lines = label.split('\n')
            width = metrics.width(max(lines)) # longest line
            height = metrics.height() * len(lines)
            # lp is the position of the center of the text
            pos = self.mapFromScene(*self.edge['lp'])
            if not self.text_label:
                self.text_label = QGraphicsTextItem(
                                 self.edge.get('label', ''), parent=self)
                self.text_label.setX(pos.x() - width / 2)
                self.text_label.setY(pos.y() - height / 2)
                self.text_label.setFont(font)
                # Make horizontal center alignment, as dot does
                self.text_label.setTextWidth(
                        self.text_label.boundingRect().width())
                fmt = QTextBlockFormat()
                fmt.setAlignment(Qt.AlignHCenter)
                cursor = self.text_label.textCursor()
                cursor.select(QTextCursor.Document)
                cursor.mergeBlockFormat(fmt)
                cursor.clearSelection()
                self.text_label.setTextCursor(cursor)
                self.text_label.show()
        except KeyError:
            # no label
            pass
        self.setPath(path)

    def __str__(self):
        ''' user-friendly information about the edge coordinates '''
        return('Edge between ' + self.edge['source'].name + ' and ' +
                self.edge['target'].name + str(self.edge['spline'][0]))

    def paint(self, painter, option, widget):
        ''' Apply anti-aliasing to Edge Connections '''
        painter.setRenderHint(QPainter.Antialiasing, True)
        super(Edge, self).paint(painter, option, widget)
        # Draw lines between connection points, if visible
        if self.bezier_visible:
            painter.setPen(
                    QPen(Qt.lightGray, 0, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            points_flat = [point.center
                           for sub1 in self.bezier[1:] for point in sub1]
            painter.drawPolyline([self.source_connection.center]
                                  + points_flat + [self.end_connection.center])
