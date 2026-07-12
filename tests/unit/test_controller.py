import pytest
from chess.core.controller import handle_commands, _pixel_to_cell, _handle_print, _handle_wait, _handle_jump, _handle_click
from chess.core.session import GameEngine
from chess.entities.board import Board
from chess.config import ChessConfig


class TestPixelToCell:
    def test_converts_pixel_to_cell_coordinates(self):
        from chess.entities.board import Board
        from chess.utils.token_format import TextTokenFormat
        fmt = TextTokenFormat()
        board = Board([["."]*8 for _ in range(8)], fmt, ChessConfig)
        engine = GameEngine(board, config=ChessConfig)
        config = ChessConfig
        config.cell_size = 100
        
        row, col = _pixel_to_cell(engine, 150, 250, config)
        assert row == 2
        assert col == 1

    def test_returns_none_if_out_of_bounds(self):
        from chess.entities.board import Board
        from chess.utils.token_format import TextTokenFormat
        fmt = TextTokenFormat()
        board = Board([["."]*8 for _ in range(8)], fmt, ChessConfig)
        engine = GameEngine(board, config=ChessConfig)
        config = ChessConfig
        config.cell_size = 100
        
        result = _pixel_to_cell(engine, 1000, 1000, config)
        assert result is None


class TestHandleCommands:
    def setup_method(self):
        self.engine = GameEngine(Board([["."]*8 for _ in range(8)]))

    def test_print_board_command(self):
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        handle_commands(self.engine, ["print board"])
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        assert "." in output

    def test_wait_command_advances_engine(self):
        self.engine.request_move(0, 0, 0, 2)
        handle_commands(self.engine, ["wait 2000"])
        assert self.engine.is_moving(0, 0) is False

    def test_jump_command_requests_jump(self):
        self.engine = GameEngine(Board([["wK", ".", "."], [".", ".", "."], [".", ".", "."]]))
        handle_commands(self.engine, ["jump 50 50"])
        assert self.engine.is_airborne(0, 0) is True

    def test_click_selects_piece(self):
        engine = GameEngine(Board([["wK", ".", "."], [".", ".", "."], [".", ".", "."]]))
        handle_commands(engine, ["click 50 50"])
        assert engine.cell(0, 0) == "wK"

    def test_click_moves_selected_piece(self):
        self.engine = GameEngine(Board([["wK", ".", "."], [".", ".", "."], [".", ".", "."]]))
        ctx = {"selected": None, "game_over": False}
        handle_commands(self.engine, ["click 50 50", "click 250 50"])
        assert ctx["selected"] is None

    def test_click_ignored_after_game_over(self):
        engine = GameEngine(Board([["wR", ".", "bK"], [".", ".", "."], [".", ".", "."]]))
        engine.request_move(0, 0, 0, 2)
        engine.advance(2000)
        assert engine.game_over is True
        handle_commands(engine, ["click 50 50", "click 250 50"])
        assert engine.cell(0, 2) == "wR"
