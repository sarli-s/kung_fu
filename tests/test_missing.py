from play.entities.pieces import get_piece, Rook, Bishop, Queen
from play.entities.board import Board


class TestGetPiece:
    def test_returns_correct_piece_type(self):
        assert type(get_piece("wK")).__name__ == "King"
        assert type(get_piece("bR")).__name__ == "Rook"
        assert type(get_piece("wQ")).__name__ == "Queen"

    def test_pawn_direction_white(self):
        p = get_piece("wP")
        assert p._dir == -1

    def test_pawn_direction_black(self):
        p = get_piece("bP")
        assert p._dir == 1

    def test_invalid_token_returns_none(self):
        assert get_piece("XX") is None
        assert get_piece("w") is None


class TestGetPath:
    def test_rook_horizontal_path(self):
        assert Rook().get_path(0, 0, 0, 3) == [(0, 1), (0, 2)]

    def test_rook_vertical_path(self):
        assert Rook().get_path(0, 0, 3, 0) == [(1, 0), (2, 0)]

    def test_bishop_diagonal_path(self):
        assert Bishop().get_path(0, 0, 3, 3) == [(1, 1), (2, 2)]

    def test_queen_straight_path(self):
        assert Queen().get_path(0, 0, 0, 3) == [(0, 1), (0, 2)]

    def test_queen_diagonal_path(self):
        assert Queen().get_path(0, 0, 2, 2) == [(1, 1)]

    def test_adjacent_move_empty_path(self):
        assert Rook().get_path(0, 0, 0, 1) == []


class TestBoardIsMoving:
    def _make(self, rows):
        return Board([r.split() for r in rows])

    def test_is_moving_true_after_request(self):
        board = self._make(["wR . ."])
        board.request_move(0, 0, 0, 2)
        assert board.is_moving(0, 0) is True

    def test_is_moving_false_before_request(self):
        board = self._make(["wR . ."])
        assert board.is_moving(0, 0) is False

    def test_is_moving_false_after_advance(self):
        board = self._make(["wR . ."])
        board.request_move(0, 0, 0, 2)
        board.advance(2000)
        assert board.is_moving(0, 0) is False


class TestGameOver:
    def _make(self, rows):
        return Board([r.split() for r in rows])

    def test_capturing_king_sets_game_over(self):
        board = self._make(["wR . bK"])
        board.request_move(0, 0, 0, 2)
        board.advance(2000)
        assert board.game_over is True

    def test_no_king_capture_game_not_over(self):
        board = self._make(["wR . bR"])
        board.request_move(0, 0, 0, 2)
        board.advance(2000)
        assert board.game_over is False

    def test_click_ignored_after_game_over(self):
        from play.core.commands import handle_commands
        board = self._make(["wR . bK"])
        board.request_move(0, 0, 0, 2)
        board.advance(2000)
        assert board.game_over is True
        # further clicks should be ignored
        handle_commands(board, ["click 50 50", "click 250 50"])
        assert board.cell(0, 2) == "wR"  # nothing moved
