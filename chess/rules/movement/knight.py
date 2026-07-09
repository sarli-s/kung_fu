from chess.rules.movement.base import StepMover

_KNIGHT_STEPS = [(dr, dc) for dr in (-2, -1, 1, 2) for dc in (-2, -1, 1, 2) if abs(dr) != abs(dc)]

def make_knight(token):
    return StepMover(_KNIGHT_STEPS)
