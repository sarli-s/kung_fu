import types
import pytest

from chess.rules.engine_rules import ChessBoardRules
from chess.config import COLOR_WHITE, COLOR_BLACK, PIECE_PAWN, PIECE_QUEEN, PIECE_KING


class DummyFmt:
    def __init__(self, token):
        self._token = token

    def piece_type(self, token):
        return token[1]

    def color(self, token):
        return token[0]

    def encode(self, token):
        return token


class DummyBoard:
    def __init__(self, rows):
        self._rows = rows

    def rows(self):
        return self._rows


class DummyPiece:
    def __init__(self):
        self.mover = types.SimpleNamespace()


def test_prepare_pawn_start_row_white():
    rules = ChessBoardRules()
    piece = DummyPiece()
    fmt = DummyFmt("wP")
    board = DummyBoard(rows=8)
    # from_row equals expected start row (6)
    rules.prepare_piece("wP", piece, board, fmt, from_row=6)
    assert piece.mover.start_row == 6


def test_prepare_pawn_start_row_not_expected():
    rules = ChessBoardRules()
    piece = DummyPiece()
    fmt = DummyFmt("wP")
    board = DummyBoard(rows=8)
    rules.prepare_piece("wP", piece, board, fmt, from_row=5)
    assert piece.mover.start_row is None


def test_get_promotion_white():
    rules = ChessBoardRules()
    fmt = DummyFmt("wP")
    board = DummyBoard(rows=8)
    # last row for white is 0
    promo = rules.get_promotion("wP", 0, board, fmt)
    assert promo == fmt.encode("w" + PIECE_QUEEN)


def test_get_promotion_non_pawn():
    rules = ChessBoardRules()
    fmt = DummyFmt("wK")
    board = DummyBoard(rows=8)
    assert rules.get_promotion("wK", 0, board, fmt) is None


def test_is_royal():
    rules = ChessBoardRules()
    fmt_k = DummyFmt("wK")
    fmt_p = DummyFmt("wP")
    assert rules.is_royal("wK", fmt_k)
    assert not rules.is_royal("wP", fmt_p)
