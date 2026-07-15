from chess.rules.movement import (
    make_bishop, make_king, make_knight, make_pawn, make_queen, make_rook,
)
from chess.entities.move import Move


def test_factory_makers_return_movers():
    # token format is color+piece, e.g., 'wP' or 'bK'
    for token in ("wB", "bB"):
        m = make_bishop(token)
        assert hasattr(m, "is_legal_move")

    for token in ("wK",):
        m = make_king(token)
        assert m.is_legal_move(Move(0, 0, 1, 1))

    for token in ("wN",):
        m = make_knight(token)
        assert m.is_legal_move(Move(0, 0, 2, 1))

    for token in ("wQ",):
        m = make_queen(token)
        assert m.is_legal_move(Move(0, 0, 0, 3))

    for token in ("wR",):
        m = make_rook(token)
        assert m.is_legal_move(Move(0, 0, 3, 0))

    # pawn forward depends on token color
    wp = make_pawn("wP")
    bp = make_pawn("bP")
    assert wp.forward[0] == -1
    assert bp.forward[0] == 1
