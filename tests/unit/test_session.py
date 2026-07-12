import pytest
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.entities.pieces.factory import PieceFactory
from chess.rules.engine_rules import ChessBoardRules
from chess.config import ChessConfig


class TestGameEngineInit:
    def test_initializes_with_board(self):
        board = Board([["."]*8 for _ in range(8)])
        engine = GameEngine(board)
        assert engine.rows() == 8
        assert engine.cols() == 8

    def test_initializes_with_default_factory(self):
        board = Board([["."]*8 for _ in range(8)])
        engine = GameEngine(board)
        assert engine._piece_factory is not None

    def test_initializes_with_default_rules(self):
        board = Board([["."]*8 for _ in range(8)])
        engine = GameEngine(board)
        assert isinstance(engine._rules, ChessBoardRules)

    def test_initializes_with_default_config(self):
        board = Board([["."]*8 for _ in range(8)])
        engine = GameEngine(board)
        assert engine._config == ChessConfig


class TestPublicReadInterface:
    def test_cell_returns_cell_content(self):
        board = Board([["wR", "."], [".", "bK"]])
        engine = GameEngine(board)
        assert engine.cell(0, 0) == "wR"
        assert engine.cell(1, 1) == "bK"

    def test_rows_returns_board_rows(self):
        board = Board([["."]*3 for _ in range(5)])
        engine = GameEngine(board)
        assert engine.rows() == 5

    def test_cols_returns_board_cols(self):
        board = Board([["."]*4 for _ in range(3)])
        engine = GameEngine(board)
        assert engine.cols() == 4

    def test_is_empty_returns_true_for_empty(self):
        board = Board([[".", "wR"], [".", "."]])
        engine = GameEngine(board)
        assert engine.is_empty(0, 0) is True
        assert engine.is_empty(1, 0) is True

    def test_is_empty_returns_false_for_occupied(self):
        board = Board([["wR", "."]])
        engine = GameEngine(board)
        assert engine.is_empty(0, 0) is False

    def test_same_color_returns_true_for_same(self):
        board = Board([["wR", "wK"], [".", "."]])
        engine = GameEngine(board)
        assert engine.same_color(0, 0, 0, 1) is True

    def test_same_color_returns_false_for_different(self):
        board = Board([["wR", "bK"], [".", "."]])
        engine = GameEngine(board)
        assert engine.same_color(0, 0, 0, 1) is False


class TestRequestJump:
    def test_request_jump_adds_to_airborne(self):
        board = Board([["wK", ".", "."]])
        engine = GameEngine(board)
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is True

    def test_request_jump_ignores_empty_cell(self):
        board = Board([[".", "wK"]])
        engine = GameEngine(board)
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is False

    def test_request_jump_ignores_while_moving(self):
        board = Board([["wR", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is False

    def test_request_jump_ignores_while_airborne(self):
        board = Board([["wK", ".", "."]])
        engine = GameEngine(board)
        engine.request_jump(0, 0)
        engine.request_jump(0, 0)
        assert engine.is_airborne(0, 0) is True


class TestRequestMove:
    def test_request_move_adds_to_pending(self):
        board = Board([["wR", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        assert engine.is_moving(0, 0) is True

    def test_request_move_ignores_while_moving(self):
        board = Board([["wR", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.request_move(0, 0, 0, 1)
        assert engine.is_moving(0, 0) is True

    def test_request_move_ignores_different_color_moving_piece(self):
        board = Board([["wR", "bK", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.request_move(0, 1, 0, 2)
        assert engine.cell(0, 1) == "bK"


class TestAdvance:
    def test_advance_moves_piece_after_duration(self):
        board = Board([["wR", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.cell(0, 0) == "."
        assert engine.cell(0, 2) == "wR"

    def test_advance_does_not_move_before_duration(self):
        board = Board([["wR", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.advance(500)
        assert engine.cell(0, 0) == "wR"
        assert engine.cell(0, 2) == "."

    def test_advance_with_multiple_cells(self):
        board = Board([["wR", ".", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 3)
        engine.advance(3000)
        assert engine.cell(0, 0) == "."
        assert engine.cell(0, 3) == "wR"


class TestExecuteMove:
    def test_execute_move_captures_enemy(self):
        board = Board([["wR", ".", "bK"]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.cell(0, 2) == "wR"
        assert engine.game_over is True

    def test_execute_move_does_not_capture_same_color(self):
        board = Board([["wR", ".", "wK"]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.cell(0, 0) == "wR"
        assert engine.cell(0, 2) == "wK"

    def test_execute_move_blocked_by_piece(self):
        board = Board([["wR", "bK", "."]])
        engine = GameEngine(board)
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.cell(0, 0) == "wR"
        assert engine.cell(0, 2) == "."

    def test_execute_move_promotes_pawn(self):
        board = Board([[".", ".", "bK"], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], ["wP", ".", "."]])
        engine = GameEngine(board)
        engine.request_move(7, 0, 6, 0)
        engine.advance(1000)
        assert engine.cell(6, 0) == "wP"
        assert engine.cell(7, 0) == "."
        engine.request_move(6, 0, 5, 0)
        engine.advance(1000)
        assert engine.cell(5, 0) == "wP"
        assert engine.cell(6, 0) == "."
        engine.request_move(5, 0, 4, 0)
        engine.advance(1000)
        assert engine.cell(4, 0) == "wP"
        assert engine.cell(5, 0) == "."
        engine.request_move(4, 0, 3, 0)
        engine.advance(1000)
        assert engine.cell(3, 0) == "wP"
        assert engine.cell(4, 0) == "."
        engine.request_move(3, 0, 2, 0)
        engine.advance(1000)
        assert engine.cell(2, 0) == "wP"
        assert engine.cell(3, 0) == "."
        engine.request_move(2, 0, 1, 0)
        engine.advance(1000)
        assert engine.cell(1, 0) == "wP"
        assert engine.cell(2, 0) == "."
        engine.request_move(1, 0, 0, 0)
        engine.advance(1000)
        assert engine.cell(0, 0) == "wQ"
        assert engine.cell(1, 0) == "."


class TestEvents:
    def test_emits_on_capture(self):
        board = Board([["wR", ".", "bR"]])
        engine = GameEngine(board)
        captured = []
        engine.subscribe("on_capture", lambda **kwargs: captured.append(kwargs))
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert len(captured) == 1
        assert captured[0]["captured"] == "bR"

    def test_emits_on_promotion(self):
        board = Board([[".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], [".", ".", "."], ["wP", ".", "."]])
        engine = GameEngine(board)
        promoted = []
        engine.subscribe("on_promotion", lambda **kwargs: promoted.append(kwargs))
        engine.request_move(7, 0, 6, 0)
        engine.advance(1000)
        engine.request_move(6, 0, 5, 0)
        engine.advance(1000)
        engine.request_move(5, 0, 4, 0)
        engine.advance(1000)
        engine.request_move(4, 0, 3, 0)
        engine.advance(1000)
        engine.request_move(3, 0, 2, 0)
        engine.advance(1000)
        engine.request_move(2, 0, 1, 0)
        engine.advance(1000)
        engine.request_move(1, 0, 0, 0)
        engine.advance(1000)
        assert len(promoted) == 1
        assert promoted[0]["piece"] == "wQ"

    def test_emits_on_game_over(self):
        board = Board([["wR", ".", "bK"]])
        engine = GameEngine(board)
        game_over = []
        engine.subscribe("on_game_over", lambda **kwargs: game_over.append(kwargs))
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert len(game_over) == 1
        assert game_over[0]["winner"] == "w"
