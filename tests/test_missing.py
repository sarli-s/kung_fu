from chess.entities.pieces import get_piece, PieceFactory, SlideMover, CHESS_PIECE_DESCRIPTORS
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.entities.move import Move


def _make_engine(rows):
    return GameEngine(Board([r.split() for r in rows]))


class TestGetPiece:
    def test_returns_correct_piece_type(self):
        assert type(get_piece("wK").mover).__name__ == "StepMover"
        assert type(get_piece("bR").mover).__name__ == "SlideMover"
        assert type(get_piece("wQ").mover).__name__ == "SlideMover"

    def test_pawn_direction_white(self):
        p = get_piece("wP")
        assert p.mover.forward == (-1, 0)

    def test_pawn_direction_black(self):
        p = get_piece("bP")
        assert p.mover.forward == (1, 0)

    def test_invalid_token_returns_none(self):
        assert get_piece("XX") is None
        assert get_piece("w") is None


class TestGetPath:
    def test_rook_horizontal_path(self):
        assert get_piece("wR").get_path(Move(0, 0, 0, 3)) == [(0, 1), (0, 2)]

    def test_rook_vertical_path(self):
        assert get_piece("wR").get_path(Move(0, 0, 3, 0)) == [(1, 0), (2, 0)]

    def test_bishop_diagonal_path(self):
        assert get_piece("wB").get_path(Move(0, 0, 3, 3)) == [(1, 1), (2, 2)]

    def test_queen_straight_path(self):
        assert get_piece("wQ").get_path(Move(0, 0, 0, 3)) == [(0, 1), (0, 2)]

    def test_queen_diagonal_path(self):
        assert get_piece("wQ").get_path(Move(0, 0, 2, 2)) == [(1, 1)]

    def test_adjacent_move_empty_path(self):
        assert get_piece("wR").get_path(Move(0, 0, 0, 1)) == []


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
        from chess.core.controller import handle_commands
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
