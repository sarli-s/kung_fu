import pytest
from unittest.mock import Mock, patch
from chess.ui.input_handler import InputHandler
import cv2


def test_input_handler_init():
    engine = Mock()
    ctx = {"selected": None, "hover": None, "game_over": False}
    
    handler = InputHandler(engine, ctx)
    
    assert handler.engine is engine
    assert handler.ctx is ctx


def test_on_mouse_event_move():
    engine = Mock()
    ctx = {"selected": None, "hover": None, "game_over": False}
    handler = InputHandler(engine, ctx)
    
    with patch('chess.ui.input_handler._pixel_to_cell', return_value=(3, 4)):
        handler.on_mouse_event(cv2.EVENT_MOUSEMOVE, 400, 300, 0, None)
    
    assert ctx["hover"] == (3, 4)


def test_on_mouse_event_move_outside_board():
    engine = Mock()
    ctx = {"selected": None, "hover": None, "game_over": False}
    handler = InputHandler(engine, ctx)
    
    with patch('chess.ui.input_handler._pixel_to_cell', return_value=None):
        handler.on_mouse_event(cv2.EVENT_MOUSEMOVE, 400, 300, 0, None)
    
    assert ctx["hover"] is None


def test_on_mouse_event_click_game_over():
    engine = Mock()
    engine.game_over = True
    ctx = {"selected": None, "hover": None, "game_over": True}
    handler = InputHandler(engine, ctx)
    
    with patch('chess.ui.input_handler._pixel_to_cell', return_value=(3, 4)):
        with patch('chess.ui.input_handler.handle_commands') as mock_handle:
            handler.on_mouse_event(cv2.EVENT_LBUTTONDOWN, 400, 300, 0, None)
            mock_handle.assert_not_called()
