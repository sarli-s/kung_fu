import pytest
from unittest.mock import Mock
from chess.ui.motion import get_smooth_position


def test_get_smooth_position_no_move_command():
    engine = Mock()
    engine.get_move_command.return_value = None
    
    pos = get_smooth_position(engine, 2, 3)
    assert pos == (2, 3)


def test_get_smooth_position_no_checkpoints():
    engine = Mock()
    cmd = Mock()
    cmd.from_row, cmd.from_col = 0, 0
    cmd.current_row, cmd.current_col = 2, 3
    cmd.checkpoints = []
    engine.get_move_command.return_value = cmd
    
    pos = get_smooth_position(engine, 2, 3)
    assert pos == (2, 3)


def test_get_smooth_position_interpolation():
    engine = Mock()
    cmd = Mock()
    cmd.from_row, cmd.from_col = 0, 0
    cmd.current_row, cmd.current_col = 4, 4
    cmd.elapsed = 500
    cmd.checkpoints = [(0, 0, 0), (1000, 4, 4)]
    engine.get_move_command.return_value = cmd
    
    pos = get_smooth_position(engine, 4, 4)
    assert pos == (2.0, 2.0)
