import pytest

from chess.rules.movement.base import StepMover, SlideMover, PawnMover
from chess.entities.move import Move


def test_step_mover_is_legal():
    mover = StepMover(steps=[(1, 0), (0, 1)])
    assert mover.is_legal_move(Move(1, 1, 2, 1))
    assert mover.is_legal_move(Move(1, 1, 1, 2))
    assert not mover.is_legal_move(Move(1, 1, 3, 1))


def test_slide_mover_delta_and_path():
    mover = SlideMover(directions=[(1, 0), (0, 1)])
    # legal vertical move
    m = Move(0, 0, 3, 0)
    assert mover.is_legal_move(m)
    assert mover.get_path(m) == [(1, 0), (2, 0)]
    # diagonal not allowed
    assert not mover.is_legal_move(Move(0, 0, 1, 1))


def test_pawn_mover_basic_moves():
    mover = PawnMover(forward=(-1, 0), allow_double=True)
    # single forward to empty
    assert mover.is_legal_move(Move(6, 0, 5, 0), dest_empty=True)
    # double forward only when start_row matches
    mover.start_row = 6
    assert mover.is_legal_move(Move(6, 0, 4, 0), dest_empty=True)
    # capture diagonal
    assert mover.is_legal_move(Move(6, 0, 5, 1), dest_empty=False)
    # path for double
    assert mover.get_path(Move(6, 0, 4, 0)) == [(5, 0)]
