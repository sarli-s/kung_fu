from abc import ABC, abstractmethod
from chess.entities.move import Move


class Mover(ABC):
    @abstractmethod
    def is_legal_move(self, move: Move, dest_empty=True) -> bool: ...

    @abstractmethod
    def get_path(self, move: Move) -> list: ...


class StepMover(Mover):
    def __init__(self, steps):
        self.steps = steps

    def is_legal_move(self, move: Move, dest_empty=True):
        dr = move.to_row - move.from_row
        dc = move.to_col - move.from_col
        return (dr, dc) in self.steps

    def get_path(self, move: Move):
        return []


class SlideMover(Mover):
    def __init__(self, directions):
        self.directions = directions

    def _delta(self, move: Move):
        dr = move.to_row - move.from_row
        dc = move.to_col - move.from_col
        scale = max(abs(dr), abs(dc))
        if scale == 0:
            return None
        unit = (dr // scale, dc // scale)
        if unit not in self.directions:
            return None
        if abs(dr) % scale != 0 or abs(dc) % scale != 0:
            return None
        return unit

    def is_legal_move(self, move: Move, dest_empty=True):
        return self._delta(move) is not None

    def get_path(self, move: Move):
        delta = self._delta(move)
        if delta is None:
            return []
        dr, dc = delta
        r, c = move.from_row + dr, move.from_col + dc
        path = []
        while (r, c) != (move.to_row, move.to_col):
            path.append((r, c))
            r, c = r + dr, c + dc
        return path


class PawnMover(Mover):
    def __init__(self, forward, allow_double=True):
        self.forward = forward
        self.allow_double = allow_double
        self.start_row = None

    def is_legal_move(self, move: Move, dest_empty=True):
        fdr, fdc = self.forward
        dr = move.to_row - move.from_row
        dc = move.to_col - move.from_col
        if dc == 0 and dest_empty and dr == fdr:
            return True
        if self.allow_double and dc == 0 and dest_empty and dr == 2 * fdr:
            if self.start_row is not None and self.start_row == move.from_row:
                return True
        if abs(dc) == 1 and dr == fdr and not dest_empty:
            return True
        return False

    def get_path(self, move: Move):
        fdr, _ = self.forward
        if abs(move.to_row - move.from_row) == 2 and move.from_col == move.to_col:
            return [(move.from_row + fdr, move.from_col)]
        return []
