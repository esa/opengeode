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

import os
import logging
from collections import defaultdict
from itertools import chain
import re
from PySide import QtGui, QtCore

try:
    import pygraphviz as dotgraph
except ImportError:
    print('pygraphviz not found. Statechart module will not work\n'
          'If you are using Debian (or Ubuntu) you can install it from\n'
          'the official repos: sudo apt-get install python-pygraphviz')

import genericSymbols
from Connectors import Edge

RENDER_DPI = {'X': None, 'Y': None}
G_SYMBOLS = set()
EDGES = []

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Record(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond', 'Stop']
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

    def mouse_move(self, event):
        ''' Disallow moving the symbols - this scene is auto-generated '''
        pass


# pylint: disable=R0904
class Point(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz point node - used for START transition'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond', 'Stop']
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

    def mouse_move(self, event):
        ''' Disallow moving the symbols - this scene is auto-generated '''
        pass


# pylint: disable=R0904
class Diamond(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Stop']
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

    def mouse_move(self, event):
        ''' Disallow moving the symbols - this scene is auto-generated '''
        pass


# pylint: disable=R0904
class Stop(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz state exit node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = []
    _terminal_followers = []
    textbox_alignment = (QtCore.Qt.AlignTop
                         | QtCore.Qt.AlignHCenter)
    has_text_area = True

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Stop, self).__init__(x=node['pos'][0], y=node['pos'][1],
                                   text=self.name)
        self.set_shape(node['width'], node['height'])
        self.graph = graph
        # Text in statecharts is read-only:
        self.text.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QtGui.QPainterPath()
        path.lineTo(width, height)
        path.moveTo(width, 0)
        path.lineTo(0, height)
        self.setPath(path)
        super(Stop, self).set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Stop node ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        pass

    def mouse_move(self, event):
        ''' Disallow moving the symbols - this scene is auto-generated '''
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
            # Note: lp is the position of the CENTER of the label
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
    attrs = []
    for each in my_graph.subgraphs():
        # Transform cluster nodes into nodes (attributes differ)
        llx, lly, urx, ury = each.graph_attr['bb'].split(',')
        wid = float(urx) - float(llx)
        hei = float(ury) - float(lly)
        attr = {}
        attr.update(pos='{0},{1}'.format(llx, lly),
                         width=wid,
                         height=hei,
                         shape=each.graph_attr['shape'],
                         label=each.graph_attr['label'],
                         style=each.graph_attr['style'],
                         name='cluster_' + each.graph_attr['label'],
                         kind='cluster')
        attrs.append(attr)
    for node in my_graph.nodes_iter():
        if not dict(node.attr):
            continue
        node.attr.update(name=node.name)
        attrs.append(node.attr)
    for node in attrs:
        new_node = {}
        # Get the node shape attribute - default is record
        new_node['shape'] = node.get('shape') or 'record'
        # node main name
        new_node['name'] = node['name']
        try:
            # node complete label (can contain several compartments)
            properties = (
                    node['label'][1:-2].split('|')[1].replace('\\', '\n'))
            new_node['properties'] = properties
        except IndexError:
            pass
        # transform width and height from inches to pixels
        if node.get('kind', '') == 'cluster':
            new_node['width'] = node['width']
            new_node['height'] = node['height']
        else:
            new_node['width'] = float(node['width']) * RENDER_DPI['X']
            new_node['height'] = float(node['height']) * RENDER_DPI['Y']
        # get the position of the CENTER of the node
        center_pos = [float(val) for val in node['pos'].split(',')]
        # apply dpi-conversion from 72 to actual screen DPI
        center_pos[0] *= (RENDER_DPI['X'] / dpi)

        # translate y-coord from bottom-left to top-left corner
        center_pos[1] = (bb_height - center_pos[1]) * (RENDER_DPI['Y'] / dpi)
        new_node['pos'] = [center_pos[0] - (new_node['width'] / 2.0),
                           center_pos[1] - (new_node['height'] / 2.0)]
        nodes.append(new_node)
    return nodes


def update(scene):
    '''
        Parse the graph symbols and create a graphviz graph
        Used to update the edges in case user moves nodes.
        This function is disabled because move of symbols is not possible
        anymore.
    '''
    return
    nodes = [{'name':node.name, 'pos':
        node.mapToScene(node.boundingRect().center()),
        'shape': type(node), 'width': node.boundingRect().width(),
        'height': node.boundingRect().height()}
        for node in scene.visible_symb if isinstance(node,
                                               (Point, Diamond, Record, Stop))]
    graph = dotgraph.AGraph(
            strict=False, directed=True, splines='spline', start='rand')

    lookup = {Point: 'point', Record: 'record',
              Diamond: 'diamond', Stop: 'square'}
    for node in nodes:
        center_pos = node['pos']
        bb_height = scene.itemsBoundingRect().height()

        dpi = 72.0

        # Convert to graphviz coordinates / adapt DPI
        center_x = center_pos.x() * (dpi / RENDER_DPI['X'])
        center_y = (bb_height - center_pos.y()) * (dpi / RENDER_DPI['Y'])

        pos = unicode('{x},{y}'.format(x=float(center_x), y=float(center_y)))

        if node['shape'] in (Point, Diamond, Stop):
            graph.add_node(node['name'], pos=pos, shape=lookup[node['shape']],
                fixedsize='true', width=node['width'] / RENDER_DPI['X'],
                height=node['height'] / RENDER_DPI['Y'], pin=True)
        else:
            graph.add_node(node['name'], pos=pos, pin=True,
                           shape=lookup[node['shape']])

    # Keep edges from the previous graph
    for edge in EDGES:
        graph.add_edge(edge, label=edge.attr.get('label') or '')

    #print graph.to_string()
    if nodes:
        before = scene.itemsBoundingRect().center()
        #before_pos = graph.get_node(nodes[0]['name']).attr['pos']
        render_statechart(scene, {'graph': graph, 'children': {}},
                          keep_pos=True)
        #after_pos = graph.get_node(nodes[0]['name']).attr['pos']
        #print before_pos,after_pos
        delta = scene.itemsBoundingRect().center() - before
        # graphviz translates the graph to pos (0, 0) -> move it back
        # to the exact graphical position where the user clicked
        for item in scene.visible_symb:
            item.position = QtCore.QPointF(item.position - delta)


def render_statechart(scene, graphtree=None, keep_pos=False, dump_gfx=''):
    ''' Render a graphviz/dot statechart on the QGraphicsScene
        set a filename to "dump_gfx" parameter to create a PNG of the graph
        input is resulting from sdl_to_statechart, it contains a tree of graphs
        in case of composite states.
    '''
    # dot uses a 72 dpi value for converting its position coordinates
    # Get actual rendering DPI from Qt view
    for view in scene.views():
        RENDER_DPI['X'] = view.physicalDpiX()
        RENDER_DPI['Y'] = view.physicalDpiY()
        break

    # Go recursive first: render children
    for aname, agraph in graphtree['children'].viewitems():
        # Render each child in a temporary scene to get the size of the scene
        # in order to resize the parent node accordingly
        temp_scene = type(scene)()
        render_statechart(temp_scene, agraph, keep_pos, dump_gfx)
        w = temp_scene.width()
        for node in graphtree['graph'].iternodes():
            if node == aname:
                size = temp_scene.itemsBoundingRect()
                node.attr['width'] = ((temp_scene.width() + 35)
                                      / RENDER_DPI['X'])
                node.attr['height'] = ((temp_scene.height() + 35)
                                      / RENDER_DPI['Y'])
                graphtree['children'][aname]['scene'] = temp_scene
                break

    # Harmonize the size of states to avoid having huge composite state(s)
    # next to single, small states. Rule: there can't be a state with a size
    # that is less than a third of the biggest state.
    try:
        min_width = float(max(node.attr.get('width', 0.0) or 0.0
                        for node in graphtree['graph'].iternodes()))
        min_height = float(max(node.attr.get('height', 0.0) or 0.0
                        for node in graphtree['graph'].iternodes()))
    except ValueError as err:
        LOG.debug(str(err))
        min_width, min_height = 0, 0
    if min_width and min_height:
        for node in graphtree['graph'].iternodes():
            if node.attr['shape'] != 'record':
                continue
            node.attr['width'] = node.attr.get('width') or (min_width / 3.0)
            node.attr['height'] = node.attr.get('height') or (min_height / 3.0)


    # Statechart symbols lookup table
    lookup = {'point': Point, 'record': Record,
              'diamond': Diamond, 'square': Stop}
    try:
        # Bonus: the tool can render any dot graph...
        graph = graphtree.get('graph', None) or dotgraph.AGraph('taste.dot')
    except IOError:
        LOG.info('No statechart to display....')
        raise
    graph.graph_attr.update(dpi='72.0')
    EDGES[:] = graph.edges()

    for each in scene.visible_symb:
        each.setVisible(False)
    #scene.clear()
    #G_SYMBOLS.clear()

    # Compute all the coordinates (self-modifying function)
    # Force the fontsize of the nodes to be 12, as in OpenGEODE
    # use -n1 below to keep user-specified node coordinates
    if dump_gfx:
        dump_name = 'sc_' + os.path.basename(dump_gfx)
        dump_gfx = os.path.dirname(dump_gfx) or '.' + os.sep + dump_name
        if dump_gfx.split('.')[-1].lower() != 'png':
            dump_gfx += '.png'

    graph.layout(prog='neato', args='-Nfontsize=12, -Efontsize=8 '
                 '-Gsplines=curved -Gsep=1 -Gdpi=72 '
                 '-Gstart=random10 -Goverlap=scale '
            '-Nstyle=rounded -Nshape=record -Elen=1 {kp} {dump}'
            .format(kp='-n1' if keep_pos else '',
                    dump=('-Tpng -o' + dump_gfx) if dump_gfx else ''))
    # bb is not visible directly - extract it from the low level api:
    bounding_rect = [float(val) for val in
            dotgraph.graphviz.agget(graph.handle, 'bb').split(',')]
    dot_dpi = float(dotgraph.graphviz.agget(graph.handle, 'dpi'))

    #fontname = graph.graph_attr.get('fontname')
    #fontsize = graph.graph_attr.get('fontsize')
    #with open('statechart.dot', 'w') as output:
    #    output.write(graph.to_string())

    nodes = preprocess_nodes(graph, bounding_rect, dot_dpi)
    node_symbols = []
    for node in nodes:
        shape = node.get('shape')
        try:
            node_symbol = lookup[shape](node, graph)
            if unicode(node_symbol) in graphtree['children'] \
                    and shape == 'record':
                # Use a different color for non-terminal states
                node_symbol.setBrush(QtGui.QBrush(QtGui.QColor(249, 249, 249)))
            G_SYMBOLS.add(node_symbol)
            node_symbols.append(node_symbol)
            scene.addItem(node_symbol)
        except KeyError:
            raise TypeError('Statechart - unsupported shape: ' + shape)
    edges = preprocess_edges(graph, node_symbols, bounding_rect, dot_dpi)

    for edge in edges:
        Edge(edge, graph)

    # Make sure the scene has no negative coordinates
    scene.translate_to_origin()

    for aname, agraph in graphtree['children'].viewitems():
        # At the end, place the content of the scene of the composite states
        # in the symbol by moving them from their temporary scene
        for symb in scene.visible_symb:
            if unicode(symb) == aname:
                deltapos = symb.scenePos() + QtCore.QPointF(30.0, 30.0)
                for each in agraph['scene'].floating_symb:
                    # In principle we should change the parentItem to make sure
                    # that all children items are moved together with their
                    # parent. Unfortunately calls to setParentItem provoke
                    # a segfault. To be tried again when PySide is fixed...
                    #each.setParent(symb)
                    scene.addItem(each)
                    each.position += deltapos
                    each.setZValue(each.zValue() + symb.zValue() + 1)


def create_dot_graph(root_ast, basic=False):
    ''' Return a dot.AGraph item, from an ogAST.Process or child entry
        Set basic=True to generate a simple graph with at most one edge
        between two states and no diamond nodes
    '''
    graph = dotgraph.AGraph(strict=False, directed=True)
    ret = {'graph': graph, 'children': {}}
    diamond = 0
    for state in root_ast.mapping.viewkeys():
        # create a new node for each state (including nested states)
        if state.endswith('START'):
            graph.add_node(state, label='', shape='point',
                           fixedsize='true', width=10.0 / 72.0)
        else:
            graph.add_node(state, label=state, shape='record', style='rounded')

    for each in [term for term in root_ast.terminators
                 if term.kind == 'return']:
        # create a new node for each RETURN statement (in nested states)
        ident = each.inputString or ' '
        graph.add_node(ident, label=ident, shape='square', width=10.0 / 72.0)
    for state, inputs in chain(root_ast.mapping.viewitems(),
                               root_ast.cs_mapping.viewitems()):
        # Add edges
        transitions = \
            inputs if not state.endswith('START') \
                   else [root_ast.transitions[inputs]]
        # Allow simplified graph, without diamonds and with at most one
        # transition from a given state to another
        target_states = defaultdict(set)
        for trans in transitions:
            source = state
            # transition label - there can be several inputs
            try:
                # Keep only message name, remove params and newlines
                # (newlines are not supported by graphviz)
                label, = re.match(r'([^(]+)', trans.inputString).groups()
                label = label.strip().replace('\n', ' ')
            except AttributeError:
                # START transition may have no inputString
                for each in root_ast.content.named_start:
                    # each is of type ogAST.Start
                    if each.transition == trans:
                        label = each.inputString[:-6]
                        break
                else:
                    label = ''

            def find_terminators(trans):
                ''' Recursively find all NEXTSTATES and RETURN nodes '''
                next_states = [term for term in trans.terminators
                               if term.kind in ('next_state', 'return')]
                joins = [term for term in trans.terminators
                         if term.kind == 'join']
                for join in joins:
                    # JOIN - Find corresponding label
                    try:
                        corr_label, = [lab for lab in
                                       root_ast.content.floating_labels +
                                       root_ast.labels if
                                       lab.inputString.lower() ==
                                       join.inputString.lower()]
                    except ValueError:
                        LOG.error('Missing label: ' + join.inputString)
                    else:
                        # Don't recurse forever in case of livelock
                        try:
                            if corr_label.inputString != trans.inputString:
                                next_states.extend(find_terminators(corr_label))
                        except AttributeError:
                            # START transition -> no inputString
                            pass
                return set(next_states)

            # Determine the list of terminators in this transition
            next_states = find_terminators(trans)

            if len(next_states) > 1 and not basic:
                # more than one terminator - add intermediate node
                graph.add_node(str(diamond),
                               shape='diamond',
                               fixedsize='true',
                               width=15.0 / 72.0,
                               height=15.0 / 72.0, label='')
                graph.add_edge(source, str(diamond), label=label)
                source = str(diamond)
                label = ''
                diamond += 1
            for term in next_states:
                if term.inputString.strip() == '-':
                    target = state
                else:
                    target = term.inputString.lower() or ' '
                if basic:
                    target_states[target].add(label)
                else:
                    graph.add_edge(source, target, label=label)
        for target, labels in target_states.viewitems():
            # Basic mode
            graph.add_edge(source, target, label=',\n'.join(labels))
#   with open('statechart.dot', 'w') as output:
#       output.write(graph.to_string())
    #return graph
    for each in root_ast.composite_states:
        ret['children'][each.statename] = create_dot_graph(each, basic)
    return ret


if __name__ == '__main__':
    render_statechart(None)
