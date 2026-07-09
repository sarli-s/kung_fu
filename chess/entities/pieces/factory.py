from chess.entities.pieces.base import Piece
from chess.rules.movement.king import make_king
from chess.rules.movement.knight import make_knight
from chess.rules.movement.rook import make_rook
from chess.rules.movement.bishop import make_bishop
from chess.rules.movement.queen import make_queen
from chess.rules.movement.pawn import make_pawn

CHESS_PIECE_DESCRIPTORS = {
    "K": make_king,
    "N": make_knight,
    "R": make_rook,
    "B": make_bishop,
    "Q": make_queen,
    "P": make_pawn,
}


class PieceFactory:
    def __init__(self, descriptors=None):
        self._descriptors = descriptors or CHESS_PIECE_DESCRIPTORS

    def create(self, token):
        if len(token) == 2 and token[1] in self._descriptors:
            return Piece(self._descriptors[token[1]](token))
        return None

    def __call__(self, token):
        return self.create(token)


def get_piece(token):
    return PieceFactory()(token)
