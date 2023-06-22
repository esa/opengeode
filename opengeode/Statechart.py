#!/usr/bin/env python3

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2022 Maxime Perrotin
    Copyright (c) 2012-2022 European Space Agency

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
import traceback
from collections import defaultdict
from functools import partial
from itertools import chain
import re

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader

# import resource file to get the configuration widget
from . import icons

g_statechart_lock = False

try:
    import pygraphviz as dotgraph
except ImportError:
    print('pygraphviz not found. Statechart module will not work\n'
          'If you are using Debian (or Ubuntu) you can install it from\n'
          'the official repos: sudo apt-get install python3-pygraphviz')

from . import genericSymbols
from .Connectors import Edge

RENDER_DPI = {'X': 72, 'Y': 72}   # default to 72, in case there is no view
G_SYMBOLS = set()
EDGES = []

LOG = logging.getLogger(__name__)


# pylint: disable=R0904
class Record(genericSymbols.HorizontalSymbol):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond', 'Stop']
    _terminal_followers = []
    textbox_alignment = (Qt.AlignTop | Qt.AlignHCenter)

    # Minimum size for symbol
    min_size = (70, 35)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        # Keep the full path to the state (with parent state names)
        # This is needed for symbol highlightning of parallel states
        self.path = node['path']
        super().__init__(x=node['pos'][0],
                y=node['pos'][1], text=self.name)
        self.set_shape(node['width'], node['height'])
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.graph = graph
        if 'properties' in node:
            property_box = QGraphicsTextItem(self)
            property_box.setPos(5, 30)
            property_box.setPlainText(node['properties'])
        # Text in statecharts is read-only:
        self.text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.text.set_textbox_position()

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QPainterPath()
        path.moveTo(0, 25)
        path.lineTo(width, 25)
        path.addRoundedRect(0, 0, width, height, 15, 15)
        self.setPath(path)
        LOG.debug ("Set shape of state " + str(self))
        #LOG.debug(traceback.print_stack())
        super().set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        # must return the state name only, as it is used in the renderer
        # in V2, there was a separate __unicode__ function
        return self.name

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        # Discard mouse release default action (CAM, UndoCommand)
        pass

    def mouse_move(self, event):
        ''' Disallow moving the symbols - this scene is auto-generated '''
        pass


# pylint: disable=R0904
class Point(genericSymbols.HorizontalSymbol):
    ''' Graphviz point node - used for START transition'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Diamond', 'Stop']
    _terminal_followers = []
    textbox_alignment = (Qt.AlignBottom | Qt.AlignHCenter)
    has_text_area = True # False (in nested state, START can have a label)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        if len (self.name) > 5:
            #  remove the _START suffix in nested state named label
            label = self.name[0:-6]
        else:
            label=''
        super().__init__(x=node['pos'][0], y=node['pos'][1],
                text=label)
        self.set_shape(node['width'], node['height'])
        self.setBrush(QBrush(Qt.black))
        self.graph = graph
        # Text is read only
        self.text.setTextInteractionFlags(Qt.TextBrowserInteraction)

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QPainterPath()
        path.addEllipse(0, 0, width, height)
        self.setPath(path)
        super().set_shape(width, height)

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
class Diamond(genericSymbols.HorizontalSymbol):
    ''' Graphviz node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = ['Record', 'Stop']
    _terminal_followers = []
    textbox_alignment = (Qt.AlignTop
                         | Qt.AlignHCenter)
    has_text_area = False

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super().__init__(x=node['pos'][0], y=node['pos'][1])
        self.set_shape(node['width'], node['height'])
        self.graph = graph

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super().set_shape(width, height)

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
class Stop(genericSymbols.HorizontalSymbol):
    ''' Graphviz state exit node - it is floating and has no parent'''
    _unique_followers = []
    _insertable_followers = []
    _terminal_followers = []
    textbox_alignment = (Qt.AlignTop
                         | Qt.AlignHCenter)
    has_text_area = True

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super().__init__(x=node['pos'][0], y=node['pos'][1],
                                   text=self.name)
        self.set_shape(node['width'], node['height'])
        self.graph = graph
        # Text in statecharts is read-only:
        self.text.setTextInteractionFlags(Qt.TextBrowserInteraction)

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        width, height = width, height
        path = QPainterPath()
        path.lineTo(width, height)
        path.moveTo(width, 0)
        path.lineTo(0, height)
        self.setPath(path)
        super().set_shape(width, height)

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
        # node full path (for nested/parallel states)
        new_node['path'] = node['comment']
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

        pos = str('{x},{y}'.format(x=float(center_x), y=float(center_y)))

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
            item.position = QPointF(item.position - delta)


def render_statechart(scene, graphtree=None, keep_pos=False, dump_gfx=''):
    ''' Render a graphviz/dot statechart on the QGraphicsScene
        set a filename to "dump_gfx" parameter to create a PNG of the graph
        input is resulting from sdl_to_statechart, it contains a tree of graphs
        in case of composite states.
    '''
    if graphtree == None:
        raise TypeError ("Statechart.py: 'render_statechart'"
                         " called with no graph tree")
    # dot uses a 72 dpi value for converting its position coordinates
    # Get actual rendering DPI from Qt view
    for view in scene.views():
        RENDER_DPI['X'] = view.physicalDpiX()
        RENDER_DPI['Y'] = view.physicalDpiY()
        break

    # Go recursive first: render children
    count = 0
    for aname, agraph in graphtree['children'].items():
        LOG.debug("Rendering child scene: " + aname)
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
                LOG.debug ("done")
                break

    # Harmonize the size of states to avoid having huge composite state(s)
    # next to single, small states. Rule: there can't be a state with a size
    # that is less than a third of the biggest state.
    try:
        min_width = float(max(float(node.attr.get('width', 0.0) or 0.0)
                        for node in graphtree['graph'].iternodes()))
        min_height = float(max(float(node.attr.get('height', 0.0) or 0.0)
                        for node in graphtree['graph'].iternodes()))
    except ValueError as err:
        LOG.debug(str(err))
        LOG.debug(traceback.format_exc())
        min_width, min_height = 0, 0
    if min_width and min_height:
        for node in graphtree['graph'].iternodes():
            if node.attr['shape'] != 'record':
                continue
            node.attr['width']  = node.attr.get('width') or (min_width / 3.0)
            node.attr['height'] = node.attr.get('height') or (min_height / 3.0)

    # Statechart symbols lookup table
    lookup = {'point'  : Point,
              'record' : Record,
              'diamond': Diamond,
              'square' : Stop}
    try:
        # Bonus: the tool can render any dot graph...
        graph = graphtree.get('graph', None) or dotgraph.AGraph('taste.dot')
        config = " ".join("{name}={val}".format(name=name, val=val)
                for name, val in graphtree['config'].items())
    except IOError as err:
        LOG.info('No statechart to display....')
        LOG.debug(str(err))
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

    graph.layout(prog='neato', args='{cfg} {kp} {dump}'
            .format(cfg=config, kp='-n1' if keep_pos else '',
                    dump=('-Tpng -o' + dump_gfx) if dump_gfx else ''))
    # bb is not visible directly - extract it from the low level api:
    bounding_rect = [float(val) for val in
            dotgraph.graphviz.agget(graph.handle, b'bb').split(b',')]
    dot_dpi = float(dotgraph.graphviz.agget(graph.handle, b'dpi'))

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
            if str(node_symbol) in graphtree['children'] \
                    and shape == 'record':
                # Use a different color for non-terminal states
                node_symbol.setBrush(QBrush(QColor(249, 249, 249)))
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

    for aname, agraph in graphtree['children'].items():
        # At the end, place the content of the scene of the composite states
        # in the symbol by moving them from their temporary scene
        for symb in scene.visible_symb:
            if str(symb) == aname:
                deltapos = symb.scenePos() + QPointF(30.0, 30.0)
                for each in agraph['scene'].floating_symb:
                    # In principle we should change the parentItem to make sure
                    # that all children items are moved together with their
                    # parent. Unfortunately calls to setParentItem provoke
                    # a segfault. To be tried again when PySide is fixed...
                    # Update (04/2019) Workaround found (see sdlSymbols.py)
                    if symb.scene() != each.scene():
                        symb.scene().addItem(each)
                    each.setParent(symb)
                    each.position += deltapos
                    each.setZValue(each.zValue() + symb.zValue() + 1)


def lock():
    ''' Prevent multiple callers to render at the same time '''
    global g_statechart_lock
    g_statechart_lock = True

def unlock():
    ''' Prevent multiple callers to render at the same time '''
    global g_statechart_lock
    g_statechart_lock = False

def locked():
    ''' Return the lock status '''
    return g_statechart_lock


def create_dot_graph(root_ast,
                     basic=False,
                     scene=None,
                     view=None,
                     is_root=True,
                     config=None):
    ''' Return a dot.AGraph item, from an ogAST.Process or child entry
        Set basic=True to generate a simple graph with at most one edge
        between two states and no diamond nodes
        is_root is set to False for nested diagrams
    '''
    graph = dotgraph.AGraph(strict=False, directed=True)
    ret = {'graph': graph, 'children': {}, 'config': {}}
    diamond = 0

    # Define the list of input signals including timers
    if is_root:
        input_signals = {sig['name'].lower() for sig in root_ast.input_signals}
        for each in root_ast.timers:
            input_signals.add(each)
    else:
        # set by recursive caller:
        input_signals = root_ast.all_signals

    # Add the Connect parts below nested states, and continuous signals
    for each in root_ast.content.states:
        for connect in each.connects:
            input_signals |= set(connect.connect_list)
        for cs in each.continuous_signals:
            LOG.debug("Continuous signal: " + cs.trigger.inputString)
            input_signals.add("[" + cs.trigger.inputString.strip() + "]")

    # valid_inputs: list of messages to be displayed in the statecharts
    # user can remove them from the file to make cleaner diagrams
    # config_params can be set to tune the call to graphviz
    valid_inputs = set()
    config_params = {}
    identifier = getattr(root_ast, "statename", root_ast.processName)
    #LOG.info("Statechart: rendering scene " + identifier)
    #LOG.info("Input signals from model: " + str (input_signals))

    try:
        if not is_root:
            # Read config file only for the top-level diagram
            config_params = config
            # Adjust edge len for inner states. 1 is too small
            config_params["-Elen"] = "1.5"
            raise IOError
        with open (identifier + ".cfg", "r") as cfg_file:
            all_lines = (line.strip() for line in cfg_file.readlines())
        for each in all_lines:
            split = each.split()
            if len(split) == 3 and split[0] == "cfg":
                config_params[split[1]] = split[2]
            elif each:
                valid_inputs.add(each.lower())
    except IOError:
        valid_inputs = input_signals
        config_params = config_params or {"-Nfontsize" : "14",
                         "-Efontsize" : "8",
                         "-Gsplines"  : "curved",
                         "-Gsep"      : "2",
                         "-Gdpi"      : "72",
                         "-Gstart"    : "random10",
                         "-Goverlap"  : "scale",
                         "-Nstyle"    : "rounded",
                         "-Nshape"    : "record",
                         "-Elen"      : "1"}
        LOG.info ("... valid signals: " + ", ".join(valid_inputs))
    else:
        LOG.info ("Statechart settings read from " + identifier + ".cfg")
        LOG.info ("... using signals: " + ", ".join(valid_inputs))

    #LOG.debug(str(config_params))

    if scene and view:
        # Load and display a table for the user to filter out messages that
        # are not relevant to display on the statechart - and make it lighter
        # Do not repeat for substates (view is None and no cfg is saved)
        lock()
        def right(leftList, rightList):
            for each in leftList.selectedItems():
                item = leftList.takeItem(leftList.row(each))
                rightList.addItem(item)
        def left(leftList, rightList):
            for each in rightList.selectedItems():
                item = rightList.takeItem(rightList.row(each))
                leftList.addItem(item)
        loader = QUiLoader()
        ui_file = QFile(":/statechart_cfg.ui")
        ui_file.open(QFile.ReadOnly)
        dialog = loader.load(ui_file)
        dialog.setParent (view, Qt.Dialog)
        okButton = dialog.findChild(QPushButton, "okButton")
        rightButton = dialog.findChild(QToolButton, "toRight")
        leftButton = dialog.findChild(QToolButton, "toLeft")
        rightList = dialog.findChild(QListWidget, "rightList")
        leftList = dialog.findChild(QListWidget, "leftList")
        okButton.pressed.connect(dialog.accept)
        rightButton.pressed.connect(partial(right, leftList, rightList))
        leftButton.pressed.connect(partial(left, leftList, rightList))
        ui_file.close()
        rightList.addItems(list(valid_inputs))
        leftList.addItems(list(input_signals - valid_inputs))
        go = dialog.exec()
        valid_inputs.clear()
        for idx in range(rightList.count()):
            valid_inputs.add(rightList.item(idx).text())
        unlock()

    inputs_to_save = set(valid_inputs)
    for state in root_ast.mapping.keys():
        # create a new node for each state (including nested states)
        if state.endswith('START'):
            if len(state) > 5:
                label=state[0:-6]
            else:
                label=''
            graph.add_node(state,
                           label=label,
                           shape='point',
                           fixedsize='true',
                           width=10.0 / 72.0)
        else:
            # Find the path to the state, this is needed to be able to
            # highlight properly the parallel states in simulation
            for s in root_ast.content.states:
                # State may have commas or *
                statelist = [a.lower() for a in s.statelist]
                if state.lower() in statelist:
                    path = s.path
                    break
            else:
                # Should never happen
                LOG.error('Bug in statechart rendering - please report')
                path = []
            path_str = ".".join(elem.split()[1] for elem in path + [f"S {state}"]
                                if not elem.startswith("PROCESS"))
            graph.add_node(state,
                           label=state,
                           comment=path_str,
                           shape='record',
                           style='rounded')

    for each in [term for term in root_ast.terminators
                 if term.kind == 'return']:
        # create a new node for each RETURN statement (in nested states)
        ident = each.inputString.lower() or ' '
        graph.add_node(ident,
                       label='X', #ident, (no, otherwise size isn't ok)
                       shape='square',
                       width=1.0 / 72.0)

    # the AST does not contain a mapping the Connect parts below a state
    # Create it here on the spot
    connect_mapping = defaultdict(list)
    for each in root_ast.content.states:
        for stateName in each.statelist:
            connect_mapping[stateName.lower()].extend(each.connects)

    for state, inputs in chain(root_ast.mapping.items(),
                               root_ast.cs_mapping.items(),
                               connect_mapping.items()):
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
                LOG.debug("Transition trigger: " + trans.inputString.strip())
                is_cs = "[" + trans.inputString.split(';')[0].strip() + "]"
                if is_cs in valid_inputs:
                    #  Make sure continuous signal strings are not filtered
                    #  split on semicolon because of the "priority" statement
                    label = is_cs #"[" + trans.inputString.strip() + "]"
                else:
                    label, = re.match(r'([^(]+)', trans.inputString).groups()
                    label = label.strip().replace('\n', ' ')
            except AttributeError as err:
                LOG.debug ("Start transition: " + str(err))
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
                if label.lower() in valid_inputs or not label.strip():
                    graph.add_edge(source,
                                   str(diamond),
                                   label=label)
                    inputs_to_save.add(label.lower())
                source = str(diamond)
                label = ''
                diamond += 1
            for term in next_states:
                if term.inputString.strip() in ('-', '-*'):
                    target = state
                else:
                    target = term.inputString.lower() or ' '
                if basic:
                    target_states[target] |= set(label.split(','))
                else:
                    labs = set(lab.strip() for lab in label.split(',') if
                                    lab.strip().lower() in valid_inputs | {""})
                    actual = ',\n'.join(labs)
                    graph.add_edge(source,
                                   target,
                                   label=actual)
                    inputs_to_save |= set(lab.lower() for lab in labs)
        for target, labels in target_states.items():
            # Here we add the label if in valid_inputs.
            sublab = [lab.strip() for lab in labels if
                      lab.strip().lower() in valid_inputs | {""}]
            # Basic mode
            if sublab:
                label=',\n'.join(sublab)
                inputs_to_save |= set(lab.lower() for lab in sublab)
            else:
                label = ''
            graph.add_edge(source,
                           target,
                           label=label)
    # Uncomment for debugging the generated dot graph:
    #with open('statechart.dot', 'w') as output:
    #   output.write(graph.to_string())
    #return graph
    if is_root:
        with open(identifier + ".cfg", "w") as cfg_file:
            for name, value in config_params.items():
                cfg_file.write("cfg {} {}\n".format(name, value))
            for each in inputs_to_save:
                cfg_file.write(each + "\n")
    ret['config'] = config_params
    for each in root_ast.composite_states:
        LOG.debug ("Recursive generation of statechart: " + each.statename)
        # Recursively generate the graphs for nested states
        # Inherit from the list of signals from the higher level state
        #each.input_signals = root_ast.input_signals
        each.all_signals = valid_inputs
        ret['children'][each.statename] = create_dot_graph(each,
                                                          basic,
                                                          scene,
                                                          is_root=False,
                                                          config=config_params)
    return ret


if __name__ == '__main__':
    render_statechart(None)
