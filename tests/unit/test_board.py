from chess.entities.board import Board


def test_cell_and_dimensions():
    grid = [[".", "wP"], ["bK", "."]]
    b = Board(grid)
    assert b.rows() == 2
    assert b.cols() == 2
    assert b.cell(0, 0) == "."
    assert b.cell(0, 1) == "wP"


def test_is_empty_and_get_set_raw():
    grid = [[".", "."]]
    b = Board(grid)
    assert b.is_empty(0, 0)
    raw = b.get_raw(0, 0)
    b.set_raw(0, 0, b.fmt().encode("wK"))
    assert b.cell(0, 0) == "wK"


def test_same_color():
    grid = [["wP", "wK"], ["bP", "."]]
    b = Board(grid)
    assert b.same_color(0, 0, 0, 1)
    assert not b.same_color(0, 0, 1, 0)


def test_str_contains_tokens():
    grid = [["wP", "."]]
    b = Board(grid)
    s = str(b)
    assert "wP" in s
    assert "." in s
