import pytest
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.config import GameConfig


def make_engine(grid, rest_after_move=2000, rest_after_jump=1000):
    config = GameConfig(rest_after_move=rest_after_move, rest_after_jump=rest_after_jump)
    return GameEngine(Board(grid), config=config)


class TestLongRest:
    def test_long_rest_starts_after_move(self):
        engine = make_engine([["wR", ".", "."]])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)  # move completes
        assert engine.is_long_rest(0, 1) is True

    def test_long_rest_blocks_move(self):
        engine = make_engine([["wR", ".", "."]])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)  # move completes, rest starts
        engine.request_move(0, 1, 0, 2)
        assert engine.is_moving(0, 1) is False

    def test_long_rest_expires_after_duration(self):
        engine = make_engine([["wR", ".", "."]])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)  # move completes
        engine.advance(2000)  # rest expires
        assert engine.is_long_rest(0, 1) is False

    def test_move_allowed_after_long_rest_expires(self):
        engine = make_engine([["wR", ".", "."]])
        engine.request_move(0, 0, 0, 1)
        engine.advance(3000)  # 1000ms move + 2000ms rest
        engine.request_move(0, 1, 0, 2)
        assert engine.is_moving(0, 1) is True

    def test_long_rest_does_not_block_jump(self):
        engine = make_engine([["wR", ".", "."]])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)  # move completes, rest starts
        engine.request_jump(0, 1)
        assert engine.is_airborne(0, 1) is True


class TestShortRest:
    def test_short_rest_starts_after_jump(self):
        engine = make_engine([["wK", ".", "."]])
        engine.request_jump(0, 0)
        engine.advance(1000)  # jump expires
        assert engine.is_short_rest(0, 0) is True

    def test_short_rest_blocks_move(self):
        engine = make_engine([["wK", ".", "."]])
        engine.request_jump(0, 0)
        engine.advance(1000)  # jump expires, short rest starts
        engine.request_move(0, 0, 0, 1)
        assert engine.is_moving(0, 0) is False

    def test_short_rest_expires_after_duration(self):
        engine = make_engine([["wK", ".", "."]])
        engine.request_jump(0, 0)
        engine.advance(1000)  # jump expires
        engine.advance(1000)  # short rest expires
        assert engine.is_short_rest(0, 0) is False

    def test_move_allowed_after_short_rest_expires(self):
        engine = make_engine([["wK", ".", "."]])
        engine.request_jump(0, 0)
        engine.advance(1000)  # jump expires, short rest starts
        engine.advance(1000)  # short rest expires
        engine.request_move(0, 0, 0, 1)
        assert engine.is_moving(0, 0) is True

    def test_short_rest_does_not_block_jump(self):
        engine = make_engine([["wK", ".", "."]])
        engine.request_jump(0, 0)
        engine.advance(1000)  # jump expires, short rest starts
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is True
