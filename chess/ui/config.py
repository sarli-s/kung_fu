import pathlib

ASSETS_ROOT = pathlib.Path(__file__).parent.parent.parent / "assets" / "images"
BOARD_IMAGE = ASSETS_ROOT / "board.png"
PIECES_DIR = ASSETS_ROOT / "pieces3"
SQUARE_IMAGE = ASSETS_ROOT / "square.jpg"

BOARD_SIZE = 808
BOARD_ROWS = 8
BOARD_COLS = BOARD_ROWS
CELL_SIZE = BOARD_SIZE // BOARD_ROWS

DEFAULT_PIECE_STATE = "idle"
DEFAULT_SPRITE_INDEX = 0

BOARD_BORDER_X = 8
BOARD_BORDER_Y = 15

MARGINS_LEFT= 150

PIECE_STATE_MAP = {
    "airborne": "jump",
    "moving": "move",
    "short_rest": "short_rest",
    "long_rest": "long_rest",
    "idle": "idle",
}
