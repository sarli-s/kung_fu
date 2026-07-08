import pytest
from play.entities.pieces import Piece, StepMover, SlideMover, PawnMover, PieceFactory, get_piece, CHESS_PIECE_DESCRIPTORS
from play.entities.move import Move


def _king():   return Piece(CHESS_PIECE_DESCRIPTORS["K"]("wK"))
def _rook():   return Piece(CHESS_PIECE_DESCRIPTORS["R"]("wR"))
def _bishop(): return Piece(CHESS_PIECE_DESCRIPTORS["B"]("wB"))
def _knight(): return Piece(CHESS_PIECE_DESCRIPTORS["N"]("wN"))
def _queen():  return Piece(CHESS_PIECE_DESCRIPTORS["Q"]("wQ"))


class TestKing:
    def test_one_step_valid(self):
        assert _king().is_legal_move(Move(0, 0, 1, 1)) is True

    def test_two_steps_invalid(self):
        assert _king().is_legal_move(Move(0, 0, 2, 2)) is False

    def test_straight_one_step_valid(self):
        assert _king().is_legal_move(Move(0, 0, 0, 1)) is True


class TestRook:
    def test_straight_horizontal_valid(self):
        assert _rook().is_legal_move(Move(0, 0, 0, 2)) is True

    def test_straight_vertical_valid(self):
        assert _rook().is_legal_move(Move(0, 0, 2, 0)) is True

    def test_diagonal_invalid(self):
        assert _rook().is_legal_move(Move(0, 0, 1, 1)) is False


class TestBishop:
    def test_diagonal_valid(self):
        assert _bishop().is_legal_move(Move(0, 0, 2, 2)) is True

    def test_straight_invalid(self):
        assert _bishop().is_legal_move(Move(0, 0, 0, 2)) is False


class TestKnight:
    def test_L_shape_valid(self):
        assert _knight().is_legal_move(Move(0, 0, 2, 1)) is True

    def test_straight_invalid(self):
        assert _knight().is_legal_move(Move(0, 0, 0, 2)) is False

    def test_diagonal_invalid(self):
        assert _knight().is_legal_move(Move(0, 0, 2, 2)) is False


class TestQueen:
    def test_diagonal_valid(self):
        assert _queen().is_legal_move(Move(0, 0, 2, 2)) is True

    def test_straight_valid(self):
        assert _queen().is_legal_move(Move(0, 0, 0, 2)) is True

    def test_invalid_move(self):
        assert _queen().is_legal_move(Move(0, 0, 1, 2)) is False


class TestPawn:
    def _white(self):
        return Piece(PawnMover(forward=(-1, 0)))

    def _black(self):
        return Piece(PawnMover(forward=(1, 0)))

    def test_white_moves_up(self):
        assert self._white().is_legal_move(Move(2, 1, 1, 1), dest=".") is True

    def test_white_cannot_move_down(self):
        assert self._white().is_legal_move(Move(1, 1, 2, 1), dest=".") is False

    def test_black_moves_down(self):
        assert self._black().is_legal_move(Move(1, 1, 2, 1), dest=".") is True

    def test_black_cannot_move_up(self):
        assert self._black().is_legal_move(Move(2, 1, 1, 1), dest=".") is False

    def test_forward_blocked_by_enemy(self):
        assert self._white().is_legal_move(Move(2, 1, 1, 1), dest="bR") is False

    def test_diagonal_capture_valid(self):
        assert self._white().is_legal_move(Move(2, 1, 1, 0), dest="bR") is True

    def test_diagonal_capture_empty_invalid(self):
        assert self._white().is_legal_move(Move(2, 1, 1, 0), dest=".") is False

    def test_cannot_move_two_steps(self):
        assert self._white().is_legal_move(Move(3, 1, 1, 1), dest=".") is False

    def test_white_double_step_from_start_valid(self):
        p = self._white(); p.mover.start_row = 3
        assert p.is_legal_move(Move(3, 1, 1, 1), dest=".") is True

    def test_black_double_step_from_start_valid(self):
        p = self._black(); p.mover.start_row = 0
        assert p.is_legal_move(Move(0, 1, 2, 1), dest=".") is True

    def test_double_step_from_non_start_invalid(self):
        p = self._white(); p.mover.start_row = 3
        assert p.is_legal_move(Move(2, 1, 0, 1), dest=".") is False

    def test_double_step_blocked_square_not_checked_by_piece(self):
        p = self._white(); p.mover.start_row = 3
        assert p.get_path(Move(3, 1, 1, 1)) == [(2, 1)]

    def test_single_step_get_path_empty(self):
        assert self._white().get_path(Move(2, 1, 1, 1)) == []
