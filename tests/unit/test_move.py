from chess.entities.move import Move


def test_move_fields_and_equality():
    m1 = Move(0, 1, 2, 3)
    m2 = Move(0, 1, 2, 3)
    assert m1.from_row == 0
    assert m1.from_col == 1
    assert m1.to_row == 2
    assert m1.to_col == 3
    assert m1 == m2


def test_move_repr_contains_coords():
    m = Move(1, 0, 1, 2)
    r = repr(m)
    assert "from_row" in r or "1" in r
