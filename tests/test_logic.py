import pytest
from io import StringIO
import sys
from play.core.parser import parse_input, parse_board
from play.core.commands import handle_commands, _pixel_to_cell
from play.entities.board import Board


# ── parse_input ────────────────────────────────────────────────────────────────

class TestParseInput:
    def test_splits_board_and_commands(self):
        text = "Board:\nwK . .\nCommands:\nclick 50 50"
        board_lines, cmd_lines = parse_input(text)
        assert board_lines == ["wK . ."]
        assert cmd_lines == ["click 50 50"]

    def test_empty_input(self):
        board_lines, cmd_lines = parse_input("")
        assert board_lines == []
        assert cmd_lines == []

    def test_multiple_board_rows(self):
        text = "Board:\nwK . .\n. . .\nCommands:"
        board_lines, _ = parse_input(text)
        assert board_lines == ["wK . .", ". . ."]

    def test_multiple_commands(self):
        text = "Board:\nCommands:\nclick 50 50\nwait 1000\nprint board"
        _, cmd_lines = parse_input(text)
        assert cmd_lines == ["click 50 50", "wait 1000", "print board"]


# ── parse_board ────────────────────────────────────────────────────────────────

class TestParseBoard:
    def test_valid_board(self):
        board, error = parse_board(["wK . .", ". . .", ". . ."])
        assert error is None
        assert board.cell(0, 0) == "wK"
        assert board.cell(0, 1) == "."

    def test_unknown_token_returns_error(self):
        board, error = parse_board(["wK XX ."])
        assert board is None
        assert error == "ERROR UNKNOWN_TOKEN"

    def test_row_width_mismatch_returns_error(self):
        board, error = parse_board(["wK . .", ". ."])
        assert board is None
        assert error == "ERROR ROW_WIDTH_MISMATCH"

    def test_all_valid_tokens_accepted(self):
        board, error = parse_board(["wK bK wQ bQ wR bR wN bN wB bB wP bP ."])
        assert error is None


# ── Board ──────────────────────────────────────────────────────────────────────

class TestBoard:
    def _make_board(self, rows):
        return Board([row.split() for row in rows])

    def test_cell_returns_correct_token(self):
        board = self._make_board(["wK . ."])
        assert board.cell(0, 0) == "wK"
        assert board.cell(0, 1) == "."

    def test_rows_and_cols(self):
        board = self._make_board(["wK . .", ". . ."])
        assert board.rows() == 2
        assert board.cols() == 3

    def test_request_move_does_not_move_immediately(self):
        board = self._make_board(["wK . ."])
        board.request_move(0, 0, 0, 1)
        assert board.cell(0, 0) == "wK"  # still there

    def test_advance_applies_legal_move(self):
        board = self._make_board(["wK . ."])
        board.request_move(0, 0, 0, 1)
        board.advance(1000)
        assert board.cell(0, 0) == "."
        assert board.cell(0, 1) == "wK"

    def test_advance_rejects_illegal_move(self):
        board = self._make_board(["wK . .", ". . .", ". . ."])
        board.request_move(0, 0, 2, 2)  # king can't move 2 steps
        board.advance(1000)
        assert board.cell(0, 0) == "wK"  # stayed

    def test_advance_clears_pending(self):
        board = self._make_board(["wK . ."])
        board.request_move(0, 0, 0, 1)
        board.advance(1000)
        board.advance(1000)  # second advance should do nothing
        assert board.cell(0, 1) == "wK"
        assert board.cell(0, 2) == "."

    def test_str_output(self):
        board = self._make_board(["wK . .", ". . ."])
        assert str(board) == "wK . .\n. . ."


# ── _pixel_to_cell ─────────────────────────────────────────────────────────────

class TestPixelToCell:
    def _make_board(self, rows):
        return Board([row.split() for row in rows])

    def test_converts_pixel_to_cell(self):
        board = self._make_board(["wK . .", ". . .", ". . ."])
        assert _pixel_to_cell(board, 50, 50) == (0, 0)
        assert _pixel_to_cell(board, 150, 150) == (1, 1)
        assert _pixel_to_cell(board, 250, 250) == (2, 2)

    def test_out_of_bounds_returns_none(self):
        board = self._make_board(["wK . ."])
        assert _pixel_to_cell(board, 999, 999) is None


# ── handle_commands ────────────────────────────────────────────────────────────

class TestHandleCommands:
    def _make_board(self, rows):
        return Board([row.split() for row in rows])

    def test_click_selects_then_moves_on_wait(self):
        board = self._make_board(["wK . .", ". . .", ". . ."])
        handle_commands(board, ["click 50 50", "click 150 150", "wait 1000"])
        assert board.cell(0, 0) == "."
        assert board.cell(1, 1) == "wK"

    def test_click_on_empty_without_selection_does_nothing(self):
        board = self._make_board(["wK . ."])
        handle_commands(board, ["click 150 0", "wait 1000"])
        assert board.cell(0, 0) == "wK"

    def test_clicking_friendly_piece_switches_selection(self):
        board = self._make_board(["wK . wR"])
        handle_commands(board, ["click 50 0", "click 250 0", "wait 1000"])
        # wR was selected last, wK should not have moved
        assert board.cell(0, 0) == "wK"

    def test_illegal_move_leaves_board_unchanged(self):
        board = self._make_board(["wK . .", ". . .", ". . ."])
        handle_commands(board, ["click 50 50", "click 250 250", "wait 1000"])
        assert board.cell(0, 0) == "wK"  # king can't jump 2 diagonally


# ── Blockers & Capture ─────────────────────────────────────────────────────────

class TestBlockersAndCapture:
    def _run(self, board_lines, cmds):
        board, _ = parse_board(board_lines)
        out = StringIO()
        sys.stdout = out
        handle_commands(board, cmds)
        sys.stdout = sys.__stdout__
        return out.getvalue().strip()

    def test_rook_blocked_by_own_piece(self):
        result = self._run(
            ["wR wP ."],
            ["click 50 50", "click 250 50", "wait 2000", "print board"]
        )
        assert result == "wR wP ."

    def test_bishop_blocked_by_own_piece(self):
        result = self._run(
            ["wB . .", ". wP .", ". . ."],
            ["click 50 50", "click 250 250", "wait 2000", "print board"]
        )
        assert result == "wB . .\n. wP .\n. . ."

    def test_knight_jumps_over_blockers(self):
        result = self._run(
            ["wN wP .", "wP . .", ". . ."],
            ["click 50 50", "click 150 250", "wait 3000", "print board"]
        )
        assert result == ". wP .\nwP . .\n. wN ."

    def test_cannot_capture_own_piece(self):
        result = self._run(
            ["wR . wP"],
            ["click 50 50", "click 250 50", "wait 2000", "print board"]
        )
        assert result == "wR . wP"

    def test_rook_captures_enemy_at_destination(self):
        result = self._run(
            ["wR . bR"],
            ["click 50 50", "click 250 50", "wait 2000", "print board"]
        )
        assert result == ". . wR"


# ── Advanced Real-Time Interaction ─────────────────────────────────────────────

class TestAdvancedInteraction:
    def _run(self, board_lines, cmds):
        board, _ = parse_board(board_lines)
        out = StringIO()
        sys.stdout = out
        handle_commands(board, cmds)
        sys.stdout = sys.__stdout__
        return out.getvalue().strip()

    def test_enemy_collision_white_started_first(self):
        result = self._run(
            ["wR . . bR"],
            ["click 50 50", "click 350 50",
             "click 350 50", "click 50 50",
             "wait 3000", "print board"]
        )
        assert result == ". . . wR"

    def test_enemy_collision_black_started_first(self):
        result = self._run(
            ["wR . . bR"],
            ["click 350 50", "click 50 50",
             "click 50 50", "click 350 50",
             "wait 3000", "print board"]
        )
        assert result == "bR . . ."

    def test_cannot_start_move_through_friendly_piece(self):
        result = self._run(
            [". . .", "wR wP .", ". . ."],
            ["click 50 150", "click 250 150", "wait 2000", "print board"]
        )
        assert result == ". . .\nwR wP .\n. . ."

    def test_dynamic_block_tactic_not_in_common_route(self):
        result = self._run(
            [". . . .", "wQ . . bK", ". . bP .", ". . . ."],
            ["click 50 150", "click 350 150",
             "wait 200",
             "click 250 250", "click 250 150",
             "wait 3000", "print board"]
        )
        assert result == ". . . .\n. . . wQ\n. . bP .\n. . . ."

    def test_knight_cannot_land_on_friendly_piece(self):
        result = self._run(
            [". wP .", ". . .", "wN . ."],
            ["click 50 250", "click 150 50", "wait 1000", "print board"]
        )
        assert result == ". wP .\n. . .\nwN . ."

    def test_premove_does_not_execute_in_common_route(self):
        result = self._run(
            ["wR . ."],
            ["click 50 50", "click 150 50",
             "click 50 50", "click 250 50",
             "wait 2000", "print board"]
        )
        assert result == ". wR ."


# ── Pawn Special Rules ─────────────────────────────────────────────────────────

class TestPawnSpecialRules:
    def _run(self, board_lines, cmds):
        board, _ = parse_board(board_lines)
        out = StringIO()
        sys.stdout = out
        handle_commands(board, cmds)
        sys.stdout = sys.__stdout__
        return out.getvalue().strip()

    def test_white_pawn_double_step_from_start(self):
        result = self._run(
            [". . .", ". . .", ". . .", ". wP ."],
            ["click 150 350", "click 150 150", "wait 2000", "print board"]
        )
        assert result == ". . .\n. wP .\n. . .\n. . ."

    def test_white_pawn_double_step_blocked(self):
        result = self._run(
            [". . .", ". . .", ". bR .", ". wP ."],
            ["click 150 350", "click 150 150", "wait 2000", "print board"]
        )
        assert result == ". . .\n. . .\n. bR .\n. wP ."

    def test_white_pawn_double_step_from_non_start_invalid(self):
        result = self._run(
            [". . .", ". . .", ". wP .", ". . ."],
            ["click 150 250", "click 150 50", "wait 2000", "print board"]
        )
        assert result == ". . .\n. . .\n. wP .\n. . ."

    def test_white_pawn_promotes_to_queen(self):
        result = self._run(
            [". . .", ". wP ."],
            ["click 150 150", "click 150 50", "wait 1000", "print board"]
        )
        assert result == ". wQ .\n. . ."

    def test_black_pawn_promotes_to_queen(self):
        result = self._run(
            [". bP .", ". . ."],
            ["click 150 50", "click 150 150", "wait 1000", "print board"]
        )
        assert result == ". . .\n. bQ ."

    def test_promoted_queen_can_move_diagonally(self):
        result = self._run(
            [". . .", ". wP .", ". . ."],
            ["click 150 150", "click 150 50", "wait 1000",
             "click 150 50", "click 250 150", "wait 1000", "print board"]
        )
        assert result == ". . .\n. . wQ\n. . ."

