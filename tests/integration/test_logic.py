import pytest
from io import StringIO
import sys
from chess.services.input_parser import parse_input
from chess.services.board_builder import build_board
from chess.core.controller import handle_commands, _pixel_to_cell
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.utils.token_format import TokenFormat
from chess.utils.errors import UnknownTokenError, RowWidthMismatchError


def _make_engine(rows):
    return GameEngine(Board([row.split() for row in rows]))


def _run(board_lines, cmds):
    engine = build_board(board_lines)
    out = StringIO()
    sys.stdout = out
    handle_commands(engine, cmds)
    sys.stdout = sys.__stdout__
    return out.getvalue().strip()


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


# ── build_board ────────────────────────────────────────────────────────────────

class TestParseBoard:
    def test_valid_board(self):
        engine = build_board(["wK . .", ". . .", ". . ."])
        assert engine.cell(0, 0) == "wK"
        assert engine.cell(0, 1) == "."

    def test_unknown_token_returns_error(self):
        with pytest.raises(UnknownTokenError):
            build_board(["wK XX ."])

    def test_row_width_mismatch_returns_error(self):
        with pytest.raises(RowWidthMismatchError):
            build_board(["wK . .", ". ."])

    def test_all_valid_tokens_accepted(self):
        engine = build_board(["wK bK wQ bQ wR bR wN bN wB bB wP bP ."])
        assert engine is not None

    def test_build_board_accepts_custom_token_format(self):
        class CustomTokenFormat(TokenFormat):
            def encode(self, token: str):
                return (token, token)

            def decode(self, value):
                return value[0]

            def empty(self):
                return (".", ".")

            def color(self, value) -> str:
                return value[0][0]

            def piece_type(self, value) -> str:
                return value[0][1]

        engine = build_board(["wK ."], token_format=CustomTokenFormat())
        assert engine is not None
        assert engine.cell(0, 0) == "wK"
        assert engine.cell(0, 1) == "."


# ── GameEngine (Board interface) ───────────────────────────────────────────────

class TestBoard:
    def test_cell_returns_correct_token(self):
        engine = _make_engine(["wK . ."])
        assert engine.cell(0, 0) == "wK"
        assert engine.cell(0, 1) == "."

    def test_rows_and_cols(self):
        engine = _make_engine(["wK . .", ". . ."])
        assert engine.rows() == 2
        assert engine.cols() == 3

    def test_request_move_does_not_move_immediately(self):
        engine = _make_engine(["wK . ."])
        engine.request_move(0, 0, 0, 1)
        assert engine.cell(0, 0) == "wK"

    def test_advance_applies_legal_move(self):
        engine = _make_engine(["wK . ."])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)
        assert engine.cell(0, 0) == "."
        assert engine.cell(0, 1) == "wK"

    def test_advance_rejects_illegal_move(self):
        engine = _make_engine(["wK . .", ". . .", ". . ."])
        engine.request_move(0, 0, 2, 2)
        engine.advance(1000)
        assert engine.cell(0, 0) == "wK"

    def test_advance_clears_pending(self):
        engine = _make_engine(["wK . ."])
        engine.request_move(0, 0, 0, 1)
        engine.advance(1000)
        engine.advance(1000)
        assert engine.cell(0, 1) == "wK"
        assert engine.cell(0, 2) == "."

    def test_str_output(self):
        engine = _make_engine(["wK . .", ". . ."])
        assert str(engine) == "wK . .\n. . ."


# ── _pixel_to_cell ─────────────────────────────────────────────────────────────

class TestPixelToCell:
    def test_converts_pixel_to_cell(self):
        engine = _make_engine(["wK . .", ". . .", ". . ."])
        assert _pixel_to_cell(engine, 50, 50) == (0, 0)
        assert _pixel_to_cell(engine, 150, 150) == (1, 1)
        assert _pixel_to_cell(engine, 250, 250) == (2, 2)

    def test_out_of_bounds_returns_none(self):
        engine = _make_engine(["wK . ."])
        assert _pixel_to_cell(engine, 999, 999) is None


# ── handle_commands ────────────────────────────────────────────────────────────

class TestHandleCommands:
    def test_click_selects_then_moves_on_wait(self):
        engine = _make_engine(["wK . .", ". . .", ". . ."])
        handle_commands(engine, ["click 50 50", "click 150 150", "wait 1000"])
        assert engine.cell(0, 0) == "."
        assert engine.cell(1, 1) == "wK"

    def test_click_on_empty_without_selection_does_nothing(self):
        engine = _make_engine(["wK . ."])
        handle_commands(engine, ["click 150 0", "wait 1000"])
        assert engine.cell(0, 0) == "wK"

    def test_clicking_friendly_piece_switches_selection(self):
        engine = _make_engine(["wK . wR"])
        handle_commands(engine, ["click 50 0", "click 250 0", "wait 1000"])
        assert engine.cell(0, 0) == "wK"

    def test_illegal_move_leaves_board_unchanged(self):
        engine = _make_engine(["wK . .", ". . .", ". . ."])
        handle_commands(engine, ["click 50 50", "click 250 250", "wait 1000"])
        assert engine.cell(0, 0) == "wK"


# ── Blockers & Capture ─────────────────────────────────────────────────────────

class TestBlockersAndCapture:
    def test_rook_blocked_by_own_piece(self):
        assert _run(["wR wP ."], ["click 50 50", "click 250 50", "wait 2000", "print board"]) == "wR wP ."

    def test_bishop_blocked_by_own_piece(self):
        assert _run(
            ["wB . .", ". wP .", ". . ."],
            ["click 50 50", "click 250 250", "wait 2000", "print board"]
        ) == "wB . .\n. wP .\n. . ."

    def test_knight_jumps_over_blockers(self):
        assert _run(
            ["wN wP .", "wP . .", ". . ."],
            ["click 50 50", "click 150 250", "wait 3000", "print board"]
        ) == ". wP .\nwP . .\n. wN ."

    def test_cannot_capture_own_piece(self):
        assert _run(["wR . wP"], ["click 50 50", "click 250 50", "wait 2000", "print board"]) == "wR . wP"

    def test_rook_captures_enemy_at_destination(self):
        assert _run(["wR . bR"], ["click 50 50", "click 250 50", "wait 2000", "print board"]) == ". . wR"


# ── Advanced Real-Time Interaction ─────────────────────────────────────────────

class TestAdvancedInteraction:
    def test_enemy_collision_white_started_first(self):
        assert _run(
            ["wR . . bR"],
            ["click 50 50", "click 350 50", "click 350 50", "click 50 50", "wait 3000", "print board"]
        ) == ". . . wR"

    def test_enemy_collision_black_started_first(self):
        assert _run(
            ["wR . . bR"],
            ["click 350 50", "click 50 50", "click 50 50", "click 350 50", "wait 3000", "print board"]
        ) == "bR . . ."

    def test_cannot_start_move_through_friendly_piece(self):
        assert _run(
            [". . .", "wR wP .", ". . ."],
            ["click 50 150", "click 250 150", "wait 2000", "print board"]
        ) == ". . .\nwR wP .\n. . ."

    def test_dynamic_block_tactic_not_in_common_route(self):
        assert _run(
            [". . . .", "wQ . . bK", ". . bP .", ". . . ."],
            ["click 50 150", "click 350 150", "wait 200",
             "click 250 250", "click 250 150", "wait 3000", "print board"]
        ) == ". . . .\n. . . wQ\n. . bP .\n. . . ."

    def test_knight_cannot_land_on_friendly_piece(self):
        assert _run(
            [". wP .", ". . .", "wN . ."],
            ["click 50 250", "click 150 50", "wait 1000", "print board"]
        ) == ". wP .\n. . .\nwN . ."

    def test_premove_does_not_execute_in_common_route(self):
        assert _run(
            ["wR . ."],
            ["click 50 50", "click 150 50", "click 50 50", "click 250 50", "wait 2000", "print board"]
        ) == ". wR ."


# ── Pawn Special Rules ─────────────────────────────────────────────────────────

class TestPawnSpecialRules:
    def test_white_pawn_double_step_from_start(self):
        assert _run(
            [". . . .", ". . . .", ". . . .", ". wP . .", ". . . ."],
            ["click 150 350", "click 150 150", "wait 2000", "print board"]
        ) == ". . . .\n. wP . .\n. . . .\n. . . .\n. . . ."

    def test_white_pawn_double_step_blocked(self):
        assert _run(
            [". . .", ". . .", ". bR .", ". wP ."],
            ["click 150 350", "click 150 150", "wait 2000", "print board"]
        ) == ". . .\n. . .\n. bR .\n. wP ."

    def test_white_pawn_double_step_from_non_start_invalid(self):
        assert _run(
            [". . . .", ". . . .", ". wP . .", ". . . .", ". . . ."],
            ["click 150 250", "click 150 50", "wait 2000", "print board"]
        ) == ". . . .\n. . . .\n. wP . .\n. . . .\n. . . ."

    def test_white_pawn_promotes_to_queen(self):
        assert _run(
            [". . .", ". wP ."],
            ["click 150 150", "click 150 50", "wait 1000", "print board"]
        ) == ". wQ .\n. . ."

    def test_black_pawn_promotes_to_queen(self):
        assert _run(
            [". bP .", ". . ."],
            ["click 150 50", "click 150 150", "wait 1000", "print board"]
        ) == ". . .\n. bQ ."

    def test_promoted_queen_can_move_diagonally(self):
        assert _run(
            [". . .", ". wP .", ". . ."],
            ["click 150 150", "click 150 50", "wait 2000",
             "click 150 50", "click 250 150", "wait 1000", "print board"]
        ) == ". . .\n. . wQ\n. . ."
