"""Tests for command parser and move validation (stage 2d)."""

import pytest
from chess.services.board_builder import build_board
from server.command_parser import MoveValidator, JumpValidator


@pytest.fixture
def engine():
    """Create a test engine with standard starting position."""
    board_lines = [
        "bR bN bB bQ bK bB bN bR",
        "bP bP bP bP bP bP bP bP",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        "wP wP wP wP wP wP wP wP",
        "wR wN wB wK wQ wB wN wR",
    ]
    return build_board(board_lines)


class TestMoveValidator:
    def test_parse_chess_notation_valid(self, engine):
        """Parse valid chess notation."""
        validator = MoveValidator(engine)
        
        # e2e4: from e2 (col 4, row 6) to e4 (col 4, row 4)
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("e2e4")
        assert from_row == 6
        assert from_col == 4
        assert to_row == 4
        assert to_col == 4
        
        # a1a2: from a1 (col 0, row 7) to a2 (col 0, row 6)
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("a1a2")
        assert from_row == 7
        assert from_col == 0
        assert to_row == 6
        assert to_col == 0

    def test_parse_chess_notation_invalid_format(self, engine):
        """Parse invalid chess notation format."""
        validator = MoveValidator(engine)
        
        # Too short
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("e2e")
        assert from_row is None
        
        # Too long
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("e2e4e")
        assert from_row is None
        
        # Invalid column
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("i2e4")
        assert from_row is None
        
        # Invalid row
        from_row, from_col, to_row, to_col = validator.parse_chess_notation("e9e4")
        assert from_row is None

    def test_execute_move_valid(self, engine):
        """Execute a valid move."""
        validator = MoveValidator(engine)
        
        # e2e4: valid white pawn move
        valid, reason = validator.execute_move("e2e4")
        assert valid
        assert reason == "Move executed"

    def test_execute_move_invalid(self, engine):
        """Execute an invalid move."""
        validator = MoveValidator(engine)
        
        # e4e5: both empty
        valid, reason = validator.execute_move("e4e5")
        assert not valid
        assert reason == "Move rejected by engine"

    def test_execute_move_invalid_notation(self, engine):
        """Execute move with invalid notation."""
        validator = MoveValidator(engine)
        
        # Invalid format
        valid, reason = validator.execute_move("e2e")
        assert not valid
        assert reason == "Invalid notation format (expected e2e4)"

    def test_execute_move_already_moving(self, engine):
        """Execute move on piece that's already moving."""
        validator = MoveValidator(engine)
        
        # Start first move
        valid1, reason1 = validator.execute_move("e2e4")
        assert valid1
        assert reason1 == "Move executed"
        
        # Try to move same piece again while it's moving (same source cell)
        valid2, reason2 = validator.execute_move("e2e4")
        assert not valid2
        assert reason2 == "Move rejected by engine"


class TestJumpValidator:
    def test_parse_chess_notation_valid(self, engine):
        """Parse valid chess notation for jump."""
        validator = JumpValidator(engine)
        
        # e2: col 4, row 6
        row, col = validator.parse_chess_notation("e2")
        assert row == 6
        assert col == 4
        
        # a1: col 0, row 7
        row, col = validator.parse_chess_notation("a1")
        assert row == 7
        assert col == 0

    def test_parse_chess_notation_invalid_format(self, engine):
        """Parse invalid chess notation format for jump."""
        validator = JumpValidator(engine)
        
        # Too short
        row, col = validator.parse_chess_notation("e")
        assert row is None
        
        # Too long
        row, col = validator.parse_chess_notation("e2e")
        assert row is None
        
        # Invalid column
        row, col = validator.parse_chess_notation("i2")
        assert row is None

    def test_execute_jump_valid(self, engine):
        """Execute a valid jump."""
        validator = JumpValidator(engine)
        
        # e2: white pawn
        valid, reason = validator.execute_jump("e2")
        assert valid
        assert reason == "Jump executed"

    def test_execute_jump_invalid(self, engine):
        """Execute an invalid jump."""
        validator = JumpValidator(engine)
        
        # e4: empty cell
        valid, reason = validator.execute_jump("e4")
        assert not valid
        assert reason == "Jump rejected by engine"

    def test_execute_jump_invalid_notation(self, engine):
        """Execute jump with invalid notation."""
        validator = JumpValidator(engine)
        
        # Invalid format
        valid, reason = validator.execute_jump("e")
        assert not valid
        assert reason == "Invalid notation format (expected e2)"

    def test_execute_jump_already_airborne(self, engine):
        """Execute jump on piece that's already airborne."""
        validator = JumpValidator(engine)
        
        # Start first jump
        valid1, reason1 = validator.execute_jump("e2")
        assert valid1
        assert reason1 == "Jump executed"
        
        # Try to jump same piece again while it's airborne (same cell)
        valid2, reason2 = validator.execute_jump("e2")
        assert not valid2
        assert reason2 == "Jump rejected by engine"
