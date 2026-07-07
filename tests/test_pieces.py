import pytest
from play.entities.pieces import King, Rook, Bishop, Knight, Queen


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
