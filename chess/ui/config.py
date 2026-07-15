import pathlib

# Paths
ASSETS_ROOT = pathlib.Path(__file__).parent.parent.parent / "assets" / "images"
BOARD_IMAGE = ASSETS_ROOT / "board.png"
PIECES_DIR = ASSETS_ROOT / "pieces3"
SQUARE_IMAGE = ASSETS_ROOT / "square.jpg"

# Board dimensions
BOARD_SIZE = 800  # pixels
CELL_SIZE = 102   # pixels (800 / 8)
BOARD_ROWS = 8
BOARD_COLS = 8

# Piece sprite state (for now, use idle)
DEFAULT_PIECE_STATE = "idle"
DEFAULT_SPRITE_INDEX = 0  # first sprite in state folder

BOARD_BORDER_X = 5
BOARD_BORDER_Y = 11

# Map engine piece states to sprite state names
PIECE_STATE_MAP = {
    "airborne": "jump",
    "moving": "move",
    "short_rest": "short_rest",
    "idle": "idle",
}
