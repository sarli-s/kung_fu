from chess.rules.movement.base import StepMover

_KING_STEPS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]

def make_king(token):
    return StepMover(_KING_STEPS)
