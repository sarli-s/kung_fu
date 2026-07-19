import pytest
from unittest.mock import Mock
from chess.ui.state_manager import get_piece_state


def test_get_piece_state_airborne():
    engine = Mock()
    engine.is_airborne.return_value = True
    engine.is_moving.return_value = False
    engine.is_short_rest.return_value = False
    engine.is_long_rest.return_value = False
    
    state = get_piece_state(engine, 0, 0)
    assert state == "jump"


def test_get_piece_state_moving():
    engine = Mock()
    engine.is_airborne.return_value = False
    engine.is_moving.return_value = True
    engine.is_short_rest.return_value = False
    engine.is_long_rest.return_value = False
    
    state = get_piece_state(engine, 0, 0)
    assert state == "move"


def test_get_piece_state_short_rest():
    engine = Mock()
    engine.is_airborne.return_value = False
    engine.is_moving.return_value = False
    engine.is_short_rest.return_value = True
    engine.is_long_rest.return_value = False
    
    state = get_piece_state(engine, 0, 0)
    assert state == "short_rest"


def test_get_piece_state_long_rest():
    engine = Mock()
    engine.is_airborne.return_value = False
    engine.is_moving.return_value = False
    engine.is_short_rest.return_value = False
    engine.is_long_rest.return_value = True
    
    state = get_piece_state(engine, 0, 0)
    assert state == "long_rest"


def test_get_piece_state_idle():
    engine = Mock()
    engine.is_airborne.return_value = False
    engine.is_moving.return_value = False
    engine.is_short_rest.return_value = False
    engine.is_long_rest.return_value = False
    
    state = get_piece_state(engine, 0, 0)
    assert state == "idle"
