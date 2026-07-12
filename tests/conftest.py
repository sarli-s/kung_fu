import pytest
from io import StringIO
import sys
from chess.services.board_builder import build_board
from chess.core.controller import handle_commands
from chess.core.session import GameEngine
from chess.entities.board import Board


@pytest.fixture
def make_engine():
    """Fixture to create a GameEngine with a board from row strings."""
    def _make_engine(rows):
        return GameEngine(Board([r.split() for r in rows]))
    return _make_engine


@pytest.fixture
def run_commands():
    """Fixture to run board_lines and commands, capturing printed output."""
    def _run(board_lines, cmds):
        engine = build_board(board_lines)
        out = StringIO()
        sys.stdout = out
        handle_commands(engine, cmds)
        sys.stdout = sys.__stdout__
        return out.getvalue().strip()
    return _run
