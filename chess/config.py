from dataclasses import dataclass, field

MOVE_TIME_PER_CELL = 1000
JUMP_DURATION = 1000
CELL_SIZE = 100

EMPTY_CELL = "."
COLOR_WHITE = "w"
COLOR_BLACK = "b"
PIECE_KING = "K"
PIECE_PAWN = "P"
PIECE_QUEEN = "Q"

PIECE_VALUES = {"Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

VALID_TOKENS = {
    EMPTY_CELL,
    "wK", "bK", "wQ", "bQ", "wR", "bR", "wN", "bN", "wB", "bB", "wP", "bP"
}


REST_AFTER_MOVE = 2000
REST_AFTER_JUMP = 1000


@dataclass
class GameConfig:
    move_time_per_cell: int = MOVE_TIME_PER_CELL
    jump_duration: int = JUMP_DURATION
    cell_size: int = CELL_SIZE
    valid_tokens: set = field(default_factory=lambda: set(VALID_TOKENS))
    rest_after_move: int = REST_AFTER_MOVE
    rest_after_jump: int = REST_AFTER_JUMP


ChessConfig = GameConfig()
