import pytest
from play.entities.pieces import King, Rook, Bishop, Knight, Queen, Pawn


class TestKing:
    def test_one_step_valid(self):
        assert King().is_legal_move(0, 0, 1, 1) is True

    def test_two_steps_invalid(self):
        assert King().is_legal_move(0, 0, 2, 2) is False

    def test_straight_one_step_valid(self):
        assert King().is_legal_move(0, 0, 0, 1) is True


class TestRook:
    def test_straight_horizontal_valid(self):
        assert Rook().is_legal_move(0, 0, 0, 2) is True

    def test_straight_vertical_valid(self):
        assert Rook().is_legal_move(0, 0, 2, 0) is True

    def test_diagonal_invalid(self):
        assert Rook().is_legal_move(0, 0, 1, 1) is False


class TestBishop:
    def test_diagonal_valid(self):
        assert Bishop().is_legal_move(0, 0, 2, 2) is True

    def test_straight_invalid(self):
        assert Bishop().is_legal_move(0, 0, 0, 2) is False


class TestKnight:
    def test_L_shape_valid(self):
        assert Knight().is_legal_move(0, 0, 2, 1) is True

    def test_straight_invalid(self):
        assert Knight().is_legal_move(0, 0, 0, 2) is False

    def test_diagonal_invalid(self):
        assert Knight().is_legal_move(0, 0, 2, 2) is False


class TestQueen:
    def test_diagonal_valid(self):
        assert Queen().is_legal_move(0, 0, 2, 2) is True

    def test_straight_valid(self):
        assert Queen().is_legal_move(0, 0, 0, 2) is True

    def test_invalid_move(self):
        assert Queen().is_legal_move(0, 0, 1, 2) is False


class TestPawn:
    def _white(self):
        p = Pawn(); p._dir = -1; return p

    def _black(self):
        p = Pawn(); p._dir = 1; return p

    def test_white_moves_up(self):
        assert self._white().is_legal_move(2, 1, 1, 1, dest=".") is True

    def test_white_cannot_move_down(self):
        assert self._white().is_legal_move(1, 1, 2, 1, dest=".") is False

    def test_black_moves_down(self):
        assert self._black().is_legal_move(1, 1, 2, 1, dest=".") is True

    def test_black_cannot_move_up(self):
        assert self._black().is_legal_move(2, 1, 1, 1, dest=".") is False

    def test_forward_blocked_by_enemy(self):
        assert self._white().is_legal_move(2, 1, 1, 1, dest="bR") is False

    def test_diagonal_capture_valid(self):
        assert self._white().is_legal_move(2, 1, 1, 0, dest="bR") is True

    def test_diagonal_capture_empty_invalid(self):
        assert self._white().is_legal_move(2, 1, 1, 0, dest=".") is False

    def test_cannot_move_two_steps(self):
        assert self._white().is_legal_move(3, 1, 1, 1, dest=".") is False
