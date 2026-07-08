from play.entities.move import Move


# ── Movement descriptors ───────────────────────────────────────────────────────

class StepMover:
    """Moves to a square reachable by exactly one of the listed (dr, dc) offsets."""
    def __init__(self, steps):
        self.steps = steps  # list of exact (dr, dc) offsets

    def is_legal_move(self, move: Move, dest="."):
        dr = move.to_row - move.from_row
        dc = move.to_col - move.from_col
        return (dr, dc) in self.steps

    def get_path(self, move: Move):
        return []


class SlideMover:
    """Slides any number of squares along allowed (dr,dc) directions."""
    def __init__(self, directions):
        self.directions = directions  # list of (dr, dc) unit vectors

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

    def is_legal_move(self, move: Move, dest="."):
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


class PawnMover:
    """
    Pawn-like mover. `forward` is the (dr, dc) of a normal step.
    Supports optional double-step from `start_row` and diagonal capture.
    """
    def __init__(self, forward, allow_double=True):
        self.forward = forward        # e.g. (-1, 0) for white
        self.allow_double = allow_double
        self.start_row = None         # set by BoardRules.prepare_piece

    def is_legal_move(self, move: Move, dest="."):
        fdr, fdc = self.forward
        dr = move.to_row - move.from_row
        dc = move.to_col - move.from_col
        # normal forward step
        if dc == 0 and dest == "." and dr == fdr:
            return True
        # double step from start row
        if self.allow_double and dc == 0 and dest == "." and dr == 2 * fdr:
            if self.start_row is not None and self.start_row == move.from_row:
                return True
        # diagonal capture
        if abs(dc) == 1 and dr == fdr and dest != ".":
            return True
        return False

    def get_path(self, move: Move):
        fdr, _ = self.forward
        if abs(move.to_row - move.from_row) == 2 and move.from_col == move.to_col:
            return [(move.from_row + fdr, move.from_col)]
        return []


# ── Generic Piece ──────────────────────────────────────────────────────────────

class Piece:
    def __init__(self, mover):
        self.mover = mover

    def is_legal_move(self, move: Move, dest="."):
        return self.mover.is_legal_move(move, dest)

    def get_path(self, move: Move):
        return self.mover.get_path(move)


# ── Default chess descriptors ──────────────────────────────────────────────────

_KING_STEPS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
_KNIGHT_STEPS = [(dr, dc) for dr in (-2, -1, 1, 2) for dc in (-2, -1, 1, 2) if abs(dr) != abs(dc)]
_ROOK_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
_BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
_QUEEN_DIRS = _ROOK_DIRS + _BISHOP_DIRS

CHESS_PIECE_DESCRIPTORS = {
    "K": lambda token: StepMover(_KING_STEPS),
    "N": lambda token: StepMover(_KNIGHT_STEPS),
    "R": lambda token: SlideMover(_ROOK_DIRS),
    "B": lambda token: SlideMover(_BISHOP_DIRS),
    "Q": lambda token: SlideMover(_QUEEN_DIRS),
    "P": lambda token: PawnMover(forward=(-1, 0) if token[0] == "w" else (1, 0)),
}


# ── Factory ────────────────────────────────────────────────────────────────────

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
    return PieceFactory().create(token)
