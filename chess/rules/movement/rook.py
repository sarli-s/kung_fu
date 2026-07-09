from chess.rules.movement.base import SlideMover

_ROOK_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def make_rook(token):
    return SlideMover(_ROOK_DIRS)
