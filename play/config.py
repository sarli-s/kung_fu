from dataclasses import dataclass, field

MOVE_TIME_PER_CELL = 1000  # ms per cell
JUMP_DURATION = 1000       # ms
CELL_SIZE = 100            # pixels per cell

EMPTY_CELL = "."
COLOR_WHITE = "w"
COLOR_BLACK = "b"
PIECE_KING = "K"
PIECE_PAWN = "P"
PIECE_QUEEN = "Q"

VALID_TOKENS = {
    EMPTY_CELL,
    "wK", "bK", "wQ", "bQ", "wR", "bR", "wN", "bN", "wB", "bB", "wP", "bP"
}


@dataclass
class GameConfig:
    move_time_per_cell: int = MOVE_TIME_PER_CELL
    jump_duration: int = JUMP_DURATION
    cell_size: int = CELL_SIZE
    valid_tokens: set = field(default_factory=lambda: set(VALID_TOKENS))


ChessConfig = GameConfig()
