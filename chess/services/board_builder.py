from chess.entities.board import Board
from chess.core.session import GameEngine
from chess.config import ChessConfig
from chess.utils.token_format import TextTokenFormat
from chess.utils.errors import UnknownTokenError, RowWidthMismatchError


def build_board(board_lines, config=None, token_format=None):
    cfg = config or ChessConfig
    fmt = token_format or TextTokenFormat()
    grid = []
    for line in board_lines:
        row = line.split()
        for token in row:
            if token not in cfg.valid_tokens:
                raise UnknownTokenError(token)
        grid.append(row)
    if grid:
        width = len(grid[0])
        for row in grid:
            if len(row) != width:
                raise RowWidthMismatchError()
    return GameEngine(Board(grid, token_format=fmt, config=cfg), config=cfg)
