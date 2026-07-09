from chess.rules.movement.base import SlideMover

_BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

def make_bishop(token):
    return SlideMover(_BISHOP_DIRS)
