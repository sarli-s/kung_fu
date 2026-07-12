import pytest
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.core.controller import handle_commands


def _make_engine(rows):
    return GameEngine(Board([r.split() for r in rows]))


class TestBoardIsMoving:
    def test_is_moving_true_after_request(self):
        engine = _make_engine(["wR . ."])
        engine.request_move(0, 0, 0, 2)
        assert engine.is_moving(0, 0) is True

    def test_is_moving_false_before_request(self):
        engine = _make_engine(["wR . ."])
        assert engine.is_moving(0, 0) is False

    def test_is_moving_false_after_advance(self):
        engine = _make_engine(["wR . ."])
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.is_moving(0, 0) is False


class TestGameOver:
    def test_capturing_king_sets_game_over(self):
        engine = _make_engine(["wR . bK"])
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.game_over is True

    def test_no_king_capture_game_not_over(self):
        engine = _make_engine(["wR . bR"])
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.game_over is False

    def test_click_ignored_after_game_over(self):
        engine = _make_engine(["wR . bK"])
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.game_over is True
        handle_commands(engine, ["click 50 50", "click 250 50"])
        assert engine.cell(0, 2) == "wR"


class TestJump:
    def test_jump_piece_stays_in_cell(self):
        engine = _make_engine(["wK . ."])
        engine.request_jump(0, 0)
        engine.advance(1000)
        assert engine.cell(0, 0) == "wK"

    def test_airborne_captures_arriving_enemy(self):
        engine = _make_engine(["wK bR ."])
        engine.request_jump(0, 0)
        engine.request_move(0, 1, 0, 0)
        engine.advance(1000)
        assert engine.cell(0, 0) == "wK"
        assert engine.cell(0, 1) == "."

    def test_cannot_jump_while_moving(self):
        engine = _make_engine(["wR . ."])
        engine.request_move(0, 0, 0, 2)
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is False
