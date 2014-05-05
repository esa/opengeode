#!/usr/bin/env python

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    This module is responsible for the rendering of statecharts using
    the graphviz library.

    Credits:
    Rendering algorithm to transform graphviz b-splines to to Qt bezier curves
    was developed by Steve Dodier-Lazaro (www.mupuf.org)

    Contact: maxime.perrotin@esa.int
"""

import logging
import math
from PySide import QtGui, QtCore

try:
    import pygraphviz as dotgraph
except ImportError:
    print('pygraphviz not found. Statechart module will not work\n'
          'If you are using Debian (or Ubuntu) you can install it from\n'
          'the official repos: sudo apt-get install python-pygraphviz')

import genericSymbols
from Connectors import Edge

RENDER_DPI = {'X': 93.0, 'Y': 95.0}
G_SYMBOLS = set()
EDGES = []

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Record(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond']
    _terminal_followers = []
    textbox_alignment = (QtCore.Qt.AlignTop
                         | QtCore.Qt.AlignHCenter)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Record, self).__init__(x=node['pos'][0],
                y=node['pos'][1], text=self.name)
        self.set_shape(node['width'], node['height'])
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 202)))
        self.graph = graph
        if 'properties' in node:
            property_box = QtGui.QGraphicsTextItem(self)
            property_box.setPos(5, 30)
            property_box.setPlainText(node['properties'])
        # Text in statecharts is read-only:
        self.text.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QtGui.QPainterPath()
        path.moveTo(0, 25)
        path.lineTo(width, 25)
        path.addRoundedRect(0, 0, width, height, 15, 15)
        self.setPath(path)
        super(Record, self).set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Record ' + self.name + ' at pos ' + str(self.pos()) +
               ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        # Discard mouse release default action (CAM, UndoCommand)
        pass


# pylint: disable=R0904
class Point(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz point node - used for START transition'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond']
    _terminal_followers = []
    textbox_alignment = (QtCore.Qt.AlignTop
                         | QtCore.Qt.AlignHCenter)
    has_text_area = False

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Point, self).__init__(x=node['pos'][0], y=node['pos'][1])
        self.set_shape(node['width'], node['height'])
        self.setBrush(QtGui.QBrush(QtCore.Qt.black))
        self.graph = graph
        # Text is read only
        #self.text.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QtGui.QPainterPath()
        path.addEllipse(0, 0, width, height)
        self.setPath(path)
        super(Point, self).set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Point ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        #self.scene().refresh()
        update(self.scene())


# pylint: disable=R0904
class Diamond(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record']
    _terminal_followers = []
    textbox_alignment = (QtCore.Qt.AlignTop
                         | QtCore.Qt.AlignHCenter)
    has_text_area = False

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Diamond, self).__init__(x=node['pos'][0], y=node['pos'][1])
        self.set_shape(node['width'], node['height'])
        self.graph = graph

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QtGui.QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super(Diamond, self).set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Node ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        #update(self.scene())
        pass

def edges(scene, node):
    ''' Return all edges of a given node '''
    for item in scene.items():
        if isinstance(item, Edge) and node in (
                item.edge['source'], item.edge['target']):
            yield item


# Front end part - use Graphviz to parse the input file and transform it
# pylint: disable=R0914
def preprocess_edges(my_graph, nodes, bounding_rect, dpi):
    ''' Parse edges and put them in a clean datastructure '''
    edges = []
    bb_height = bounding_rect[3]
    for edge in my_graph.edges_iter():
        new_edge = {}
        source, target = edge
        for node in nodes:
            if node.name == source:
                new_edge['source'] = node
            if node.name == target:
                new_edge['target'] = node
        new_edge['label'] = edge.attr.get('label')
        try:
            new_edge['lp'] = [float(val) for val in edge.attr['lp'].split(',')]
        except (ValueError, AttributeError):
            pass
        else:
            # translate the label position from dot-coordinates to Qt
            new_edge['lp'][0] *= RENDER_DPI['X'] / dpi
            new_edge['lp'][1] = (
                    bb_height - new_edge['lp'][1]) * (RENDER_DPI['Y'] / dpi)

        pos = edge.attr['pos'].split()

        if pos[0].startswith('e'):
            new_edge['end'] = [float(val)
                    for val in pos.pop(0).split(',')[1:]]
            # And translate position
            new_edge['end'][0] *= (RENDER_DPI['X'] / dpi)
            new_edge['end'][1] = (
                    bb_height - new_edge['end'][1]) * (RENDER_DPI['Y'] / dpi)

        elif pos[0].startswith('s'):
            new_edge['start'] = [float(val)
                    for val in pos.pop(0).split(',')[1:]]
            # And translate position
            new_edge['start'][0] *= (RENDER_DPI['X'] / dpi)
            new_edge['start'][1] = (
                    bb_height - new_edge['start'][1]) * (RENDER_DPI['Y'] / dpi)

        spline = []
        for entry in pos:
            point = [float(val) for val in entry.split(',')]
            point[0] *= (RENDER_DPI['X'] / dpi)
            point[1] = (bb_height - point[1]) * (RENDER_DPI['Y'] / dpi)

            spline.append(point)
        new_edge['spline'] = spline
        edges.append(new_edge)
    return edges


def preprocess_nodes(my_graph, bounding_rect, dpi):
    ''' Parse the nodes from the graph and create a clean datastructure '''
    # Graphviz calculates coordinates starting on the bottom-left corner,
    # while Qt uses the top-left corner, so we must translate all y-coord.
    bb_height = bounding_rect[3]
    nodes = []
    for node in my_graph.nodes_iter():
        new_node = {}
        # Get the node shape attribute - default is record
        new_node['shape'] = node.attr.get('shape') or 'record'
        # node main name
        new_node['name'] = str(node)
        try:
            # node complete label (can contain several compartments)
            properties = (
                    node.attr['label'][1:-2].split('|')[1].replace('\\', '\n'))
            new_node['properties'] = properties  # node.attr.get('label')
        except IndexError:
            pass
        # transform width and height from inches to pixels
        new_node['width'] = float(node.attr.get('width')) * RENDER_DPI['X']
        new_node['height'] = float(node.attr.get('height')) * RENDER_DPI['Y']
        # get the position of the CENTER of the node
        center_pos = [float(val)
                for val in node.attr.get('pos').split(',')]
        # apply dpi-conversion from 72 to 96
        center_pos[0] *= (RENDER_DPI['X'] / dpi)

        # translate y-coord from bottom-left to top-left corner
        center_pos[1] = (
                bb_height - center_pos[1]) * (RENDER_DPI['Y'] / dpi)
        new_node['pos'] = [center_pos[0] - (new_node['width'] / 2.0),
                           center_pos[1] - (new_node['height'] / 2.0)]
        nodes.append(new_node)
    return nodes


def update(scene):
    '''
        Parse the graph symbols and create a graphviz graph
        Used to update the edges in case user moves nodes.
    '''
    nodes = [{'name':node.name, 'pos':
        node.mapToScene(node.boundingRect().center()),
        'shape': type(node), 'width': node.boundingRect().width(),
        'height': node.boundingRect().height()}
        for node in scene.items() if isinstance(node,
                                               (Point, Diamond, Record))]
    graph = dotgraph.AGraph(
            strict=False, directed=True, splines='spline', start='rand')

    lookup = {Point: 'point', Record: 'record', Diamond: 'diamond'}
    for node in nodes:
        center_pos = node['pos']
        bb_height = scene.itemsBoundingRect().height()

        dpi = 72.0

        # Convert to graphviz coordinates / adapt DPI
        center_x = center_pos.x() * (dpi / RENDER_DPI['X'])
        center_y = (bb_height - center_pos.y()) * (dpi / RENDER_DPI['Y'])

        pos = unicode('{x},{y}'.format(x=int(center_x), y=int(center_y)))

        #print node['name'], node['height'], node['height'] / RENDER_DPI['Y']

        if node['shape'] in (Point, Diamond):
            graph.add_node(node['name'], pos=pos, shape=lookup[node['shape']],
                fixedsize='true', width=node['width'] / RENDER_DPI['X'],
                height=node['height'] / RENDER_DPI['Y'])
        else:
            graph.add_node(node['name'], pos=pos, shape=lookup[node['shape']])

    # Keep edges from the previous graph
    for edge in EDGES:
        graph.add_edge(edge, label=edge.attr.get('label') or '')

    #print graph.to_string()
    if nodes:
        #before = scene.itemsBoundingRect().center()
        render_statechart(scene, graph, keep_pos=True)
        #delta = scene.itemsBoundingRect().center() - before
        # graphviz translates the graph to pos (0, 0) -> move it back
        # to the exact graphical position where the user clicked
        #for item in scene.items():
        #    if isinstance(item, genericSymbols.Symbol):
        #        item.setPos(item.pos() - delta)


def render_statechart(scene, graph=None, keep_pos=False):
    ''' Render a graphviz/dot statechart on the QGraphicsScene '''
    # Statechart symbols lookup table
    lookup = {'point': Point, 'record': Record, 'diamond': Diamond}
    try:
        # Bonus: the tool can render any dot graph...
        graph = graph or dotgraph.AGraph('taste.dot')
    except IOError:
        LOG.info('No statechart to display....')
        raise
    graph.graph_attr.update(dpi='72.0')
    EDGES[:] = graph.edges()

    scene.clear()
    G_SYMBOLS.clear()

    # Compute all the coordinates (self-modifying function)
    # Force the fontsize of the nodes to be 12, as in OpenGEODE
    # use -n2 below to keep user-specified node coordinates
    graph.layout(prog='neato', args='-Nfontsize=12, -Gsplines=true -Gsep=1 '
            '-Gstart=random10 '
            '-Nstyle=rounded -Nshape=record -Elen=1.5 {kp}'
            .format(kp='-n1' if keep_pos else ''))
    # bb is not visible directly - extract it from the low level api:
    bounding_rect = [float(val) for val in
            dotgraph.graphviz.agget(graph.handle, 'bb').split(',')]
    dot_dpi = float(dotgraph.graphviz.agget(graph.handle, 'dpi'))
    # dot uses a 72 dpi value for converting its position coordinates
    # Get actual rendering DPI from Qt view
    for view in scene.views():
        RENDER_DPI['X'] = view.physicalDpiX()
        RENDER_DPI['Y'] = view.physicalDpiY()

    #fontname = graph.graph_attr.get('fontname')
    #fontsize = graph.graph_attr.get('fontsize')
    #print 'AFTER PROCESSING: ', graph.to_string()

    nodes = preprocess_nodes(graph, bounding_rect, dot_dpi)
    node_symbols = []
    for node in nodes:
        shape = node.get('shape')
        try:
            node_symbol = lookup[shape](node, graph)
        except KeyError:
            raise TypeError('Statechart - unsupported shape: ' + shape)
        G_SYMBOLS.add(node_symbol)
        node_symbols.append(node_symbol)
        scene.addItem(node_symbol)
    edges = preprocess_edges(graph, node_symbols, bounding_rect, dot_dpi)

    for edge in edges:
        Edge(edge, graph)


if __name__ == '__main__':
    render_statechart(None)
