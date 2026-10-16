import os
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from opengeode.opengeode import SDL_Scene, SDL_View
from opengeode.sdlSymbols import Process


@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_scrollbars_redimensioned_after_symbol_move(qapp):
    '''Test that moving a symbol and releasing the mouse redimensions the scrollbars (F5 equivalent).'''
    scene = SDL_Scene('block')
    view = SDL_View(scene)
    p = scene.place_symbol(item_type=Process, parent=None, pos=QPointF(50, 50))
    view.view_refresh()
    initial_rect = view.sceneRect()

    # Move symbol to a distant zone (2500, 2000)
    p.coord = p.position
    p.pos_x = 2500
    p.pos_y = 2000
    p.mode = 'Move'
    p.mouse_release(None)

    new_rect = view.sceneRect()
    assert new_rect.right() >= 2500, f"Expected sceneRect to expand past 2500, got {new_rect.right()}"
    assert new_rect.bottom() >= 2000, f"Expected sceneRect to expand past 2000, got {new_rect.bottom()}"
    assert new_rect.width() > initial_rect.width()
    assert new_rect.height() > initial_rect.height()


def test_scrollbars_redimensioned_on_negative_move(qapp):
    '''Test that moving a symbol to negative coordinates expands the scrollbars accordingly.'''
    scene = SDL_Scene('block')
    view = SDL_View(scene)
    p = scene.place_symbol(item_type=Process, parent=None, pos=QPointF(100, 100))
    view.view_refresh()

    # Move symbol to negative coordinates (-600, -400)
    p.coord = p.position
    p.pos_x = -600
    p.pos_y = -400
    p.mode = 'Move'
    p.mouse_release(None)

    new_rect = view.sceneRect()
    assert new_rect.left() <= -600, f"Expected sceneRect.left to be <= -600, got {new_rect.left()}"
    assert new_rect.top() <= -400, f"Expected sceneRect.top to be <= -400, got {new_rect.top()}"


def test_scrollbars_redimensioned_on_undo_redo(qapp):
    '''Test that undoing and redoing a move updates the scrollbars.'''
    scene = SDL_Scene('block')
    view = SDL_View(scene)
    p = scene.place_symbol(item_type=Process, parent=None, pos=QPointF(50, 50))
    view.view_refresh()

    p.coord = p.position
    p.pos_x = 3000
    p.pos_y = 3000
    p.mode = 'Move'
    p.mouse_release(None)

    rect_moved = view.sceneRect()
    assert rect_moved.right() >= 3000

    scene.undo_stack.undo()
    rect_undone = view.sceneRect()
    # Undoing the move moves the symbol back to (50, 50)
    assert p.pos_x == 50
    assert p.pos_y == 50

    scene.undo_stack.redo()
    rect_redone = view.sceneRect()
    assert p.pos_x == 3000
    assert rect_redone.right() >= 3000
