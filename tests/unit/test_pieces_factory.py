import pytest
from chess.entities.pieces import get_piece, PieceFactory, SlideMover, CHESS_PIECE_DESCRIPTORS
from chess.entities.move import Move


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
