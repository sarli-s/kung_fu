from chess.rules.movement.base import Mover
from chess.entities.move import Move


class Piece:
    def __init__(self, mover: Mover):
        self.mover = mover

    def is_legal_move(self, move: Move, dest_empty=True):
        return self.mover.is_legal_move(move, dest_empty)

    def get_path(self, move: Move):
        return self.mover.get_path(move)
