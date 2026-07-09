from chess.rules.movement.base import PawnMover

def make_pawn(token):
    return PawnMover(forward=(-1, 0) if token[0] == "w" else (1, 0))
