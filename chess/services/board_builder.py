from chess.entities.board import Board
from chess.core.session import GameEngine
from chess.config import ChessConfig


def build_board(board_lines, config=None):
    cfg = config or ChessConfig
    grid = []
    for line in board_lines:
        row = line.split()
        for token in row:
            if token not in cfg.valid_tokens:
                return None, "ERROR UNKNOWN_TOKEN"
        grid.append(row)
    if grid:
        width = len(grid[0])
        for row in grid:
            if len(row) != width:
                return None, "ERROR ROW_WIDTH_MISMATCH"
    return GameEngine(Board(grid, config=cfg), config=cfg), None
