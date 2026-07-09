from chess.rules.movement.base import SlideMover

_QUEEN_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

def make_queen(token):
    return SlideMover(_QUEEN_DIRS)
