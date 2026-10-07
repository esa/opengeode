#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the CIF-coordinate layout behaviour.

When a model is loaded, only the floating (top-level) symbols are placed
from the coordinates stored in the file (the CIF comments); everything
below them is laid out, then each floating symbol's sub-tree is
rebalanced (clean_layout) and collision-avoided (cam) so branches are
evenly spread and do not overlap.

Also covers:
  * the block scene's declaration textbox no longer overlapping the
    process symbols;
  * the Orbit MCP insertion (headless SdlModel.add) doing the same
    relayout + collision avoidance + F5-equivalent view refresh;
  * cam(animate=False) moving synchronously (no event loop).

Requires PySide6 (the scenes are rendered headless with it).
"""

import glob
import os
import shutil

import pytest

pytest.importorskip('PySide6')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
TESTSUITE = os.path.join(REPO, 'tests', 'testsuite')


@pytest.fixture(scope='module', autouse=True)
def qapp():
    '''A QApplication must exist before any SDL_Scene is created.'''
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _load_model(directory):
    '''Parse the model of a test directory and render its block scene,
    the way a load does. Returns the scene.'''
    from opengeode import ogParser, ogAST
    from opengeode.opengeode import SDL_Scene

    prs = sorted(glob.glob(os.path.join(directory, '*.pr')))
    struct = [p for p in prs if 'system_structure' in p]
    if struct:
        prs = [p for p in prs if 'system_structure' not in p] + struct
    cwd = os.getcwd()
    os.chdir(directory)
    try:
        ast, _warn, errors = ogParser.parse_pr(
            files=[os.path.basename(p) for p in prs])
    finally:
        os.chdir(cwd)
    assert not errors, errors
    try:
        syst, = ast.systems
        block, = syst.blocks
        if block.processes and block.processes[0].referenced:
            block.processes = list(ast.processes)
    except ValueError:
        block = ogAST.Block()
        block.processes = list(ast.processes)
    scene = SDL_Scene(context='block')
    scene.render_everything(block)
    return scene


def _flow_overlaps(scene):
    '''Pairs of *flow* symbols in the same scene whose scene rectangles
    genuinely overlap (more than a couple of pixels). Declaration text
    areas and comments are decorations, not part of the flow the layout
    tidies up, so they are not considered here (the block textbox is
    covered by its own test below).'''
    from opengeode import genericSymbols as gs, sdlSymbols
    syms = [s for s in scene.visible_symb
            if not isinstance(s, (gs.Comment, sdlSymbols.TextSymbol))]
    bad = []
    for i in range(len(syms)):
        for j in range(i + 1, len(syms)):
            a, b = syms[i], syms[j]
            ra, rb = a.sceneBoundingRect(), b.sceneBoundingRect()
            if ra.intersects(rb):
                inter = ra & rb
                if inter.width() > 3 and inter.height() > 3:
                    bad.append((str(a)[:20], str(b)[:20]))
    return bad


def _all_scenes(scene):
    '''The block scene and every nested scene reachable from it.'''
    out = []

    def visit(sc):
        if id(sc) in seen_ids:
            return
        seen_ids.add(id(sc))
        out.append(sc)
        for symb in sc.visible_symb:
            sub = getattr(symb, 'nested_scene', None)
            if sub is not None and hasattr(sub, 'visible_symb'):
                visit(sub)

    seen_ids = set()
    visit(scene)
    return out


# Models with processes, decisions and states to exercise the layout.
MODELS = ['test1', 'test2', 'test3', 'test4', 'test6', 'test7',
          'test-controlflow']


@pytest.mark.parametrize('model', MODELS)
def test_loaded_model_has_no_flow_overlaps(model):
    '''Loading spreads the branches and avoids collisions: no two flow
    symbols of the same scene overlap, at any nesting level.'''
    directory = os.path.join(TESTSUITE, model)
    if not os.path.isdir(directory):
        pytest.skip(f'{model} not present')
    scene = _load_model(directory)
    for sc in _all_scenes(scene):
        overlaps = _flow_overlaps(sc)
        assert not overlaps, (f'{model}: overlap in scene '
                              f'{sc.name!r}: {overlaps}')


def test_block_textbox_does_not_overlap_process_symbols():
    '''The block scene's generated declaration textbox used to be placed
    at the bounding-rectangle *width* instead of its right edge, so it
    landed on top of the process whenever the process was not at x=0.'''
    scene = _load_model(os.path.join(TESTSUITE, 'test1'))
    import opengeode.sdlSymbols as sdlSymbols
    texts = [s for s in scene.visible_symb
             if isinstance(s, sdlSymbols.TextSymbol)]
    processes = [s for s in scene.visible_symb
                 if getattr(s, 'common_name', '') == 'process_definition']
    assert texts and processes, 'expected a textbox and a process'
    for text in texts:
        for proc in processes:
            assert not text.sceneBoundingRect().intersects(
                proc.sceneBoundingRect()), \
                f'textbox {text!r} overlaps process {proc!r}'


def test_floating_symbols_keep_their_cif_coordinates():
    '''Only the floating symbols are placed from the file: the load must
    not translate them to the origin.'''
    scene = _load_model(os.path.join(TESTSUITE, 'test7'))
    process = next(s for s in scene.visible_symb
                   if getattr(s, 'common_name', '') == 'process_definition')
    # The CIF coordinates of the process in test7/system_structure.pr.
    assert (process.pos_x, process.pos_y) == (process.ast.pos_x,
                                              process.ast.pos_y)


def test_cam_without_animation_moves_immediately():
    '''cam(animate=False) must move the colliding symbol at once: the
    default (animated) path only moves once the Qt event loop runs,
    which never happens during a programmatic placement.'''
    from opengeode.opengeode import SDL_Scene
    from opengeode.sdlSymbols import Process

    scene = SDL_Scene(context='block')
    left, right = Process(None), Process(None)
    for symbol in (left, right):
        scene.addItem(symbol)
    from PySide6.QtCore import QPointF
    left.position = QPointF(0, 0)
    right.position = QPointF(20, 0)       # overlapping the left one
    left.cam(left.pos(), left.pos(), animate=False)
    # Without an event loop the animated move would not have happened;
    # the immediate one must have separated them.
    assert not left.sceneBoundingRect().intersects(
        right.sceneBoundingRect())


def test_cam_animated_keeps_moving_via_the_undo_stack():
    '''The default (animate=True) path is unchanged: it records a
    MoveSymbol command and defers the move - the interactive behaviour.'''
    from opengeode.opengeode import SDL_Scene
    from opengeode.sdlSymbols import Process
    from PySide6.QtCore import QPointF

    scene = SDL_Scene(context='block')
    left, right = Process(None), Process(None)
    for symbol in (left, right):
        scene.addItem(symbol)
    left.position = QPointF(0, 0)
    right.position = QPointF(20, 0)
    before = scene.undo_stack.count()
    left.cam(left.pos(), left.pos())      # animate defaults to True
    assert scene.undo_stack.count() > before   # a MoveSymbol was pushed


def test_mcp_add_relayouts_and_refreshes_the_view(tmp_path):
    '''A remote (MCP) insertion runs the same tidy-up as a manual one:
    clean_layout + collision avoidance, and the F5-equivalent view
    refresh so the scrollbars span the new diagram.'''
    from opengeode.SdlMcpServer import SdlModel
    from opengeode.opengeode import SDL_Scene

    workdir = tmp_path / 'model'
    shutil.copytree(os.path.join(TESTSUITE, 'test1'), workdir,
                    ignore=shutil.ignore_patterns('*.o', 'target', 'code*'))
    os.chdir(str(workdir))
    model = SdlModel(['og.pr', 'system_structure.pr'])

    calls = {'clean': 0, 'refresh': 0}

    from opengeode import genericSymbols
    real_clean = genericSymbols.clean_layout
    real_refresh = SDL_Scene.refresh_scrollbars

    def spy_clean(symbol):
        calls['clean'] += 1
        return real_clean(symbol)

    def spy_refresh(self):
        calls['refresh'] += 1
        return real_refresh(self)

    genericSymbols.clean_layout = spy_clean
    SDL_Scene.refresh_scrollbars = spy_refresh
    try:
        # Put the new process exactly on top of the existing one: the
        # collision avoidance must separate them.
        model.add('process', scene_name='block', text='second',
                  x=48, y=150)
    finally:
        genericSymbols.clean_layout = real_clean
        SDL_Scene.refresh_scrollbars = real_refresh

    assert calls['clean'] >= 1, 'clean_layout was not called on insert'
    assert calls['refresh'] >= 1, 'the F5-equivalent refresh was not called'

    # And no two process symbols ended up overlapping.
    processes = [s for s in model.scene.visible_symb
                 if getattr(s, 'common_name', '') == 'process_definition']
    assert len(processes) >= 2
    for i in range(len(processes)):
        for j in range(i + 1, len(processes)):
            assert not processes[i].sceneBoundingRect().intersects(
                processes[j].sceneBoundingRect()), \
                'two process symbols overlap after the insert'


def test_refresh_scrollbars_is_a_noop_headless():
    '''The F5 equivalent must not explode on a scene with no view (the
    headless MCP server renders exactly such scenes).'''
    from opengeode.opengeode import SDL_Scene
    scene = SDL_Scene(context='block')
    assert not scene.views()
    scene.refresh_scrollbars()            # must not raise


if __name__ == '__main__':
    for name, value in dict(globals()).items():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
