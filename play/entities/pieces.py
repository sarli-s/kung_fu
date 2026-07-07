class Piece:
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        raise NotImplementedError

    def get_path(self, from_row, from_col, to_row, to_col):
        """Returns list of intermediate (row, col) squares (excludes start and end)."""
        return []

class King(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        return max(abs(to_row - from_row), abs(to_col - from_col)) == 1

class Rook(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        return from_row == to_row or from_col == to_col

    def get_path(self, from_row, from_col, to_row, to_col):
        dr = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        dc = 0 if to_col == from_col else (1 if to_col > from_col else -1)
        r, c = from_row + dr, from_col + dc
        path = []
        while (r, c) != (to_row, to_col):
            path.append((r, c))
            r, c = r + dr, c + dc
        return path

class Bishop(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        return abs(to_row - from_row) == abs(to_col - from_col)

    def get_path(self, from_row, from_col, to_row, to_col):
        dr = 1 if to_row > from_row else -1
        dc = 1 if to_col > from_col else -1
        r, c = from_row + dr, from_col + dc
        path = []
        while (r, c) != (to_row, to_col):
            path.append((r, c))
            r, c = r + dr, c + dc
        return path

class Knight(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        dr, dc = abs(to_row - from_row), abs(to_col - from_col)
        return sorted([dr, dc]) == [1, 2]

class Queen(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        dr, dc = abs(to_row - from_row), abs(to_col - from_col)
        return dr == dc or from_row == to_row or from_col == to_col

    def get_path(self, from_row, from_col, to_row, to_col):
        dr = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        dc = 0 if to_col == from_col else (1 if to_col > from_col else -1)
        r, c = from_row + dr, from_col + dc
        path = []
        while (r, c) != (to_row, to_col):
            path.append((r, c))
            r, c = r + dr, c + dc
        return path

class Pawn(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col, dest="."):
        dr = to_row - from_row
        dc = abs(to_col - from_col)
        if dc == 0 and dest == ".":
            if dr == self._dir:
                return True
            if dr == 2 * self._dir and getattr(self, "_start_row", None) == from_row:
                return True
        if dc == 1 and dr == self._dir and dest != ".":
            return True
        return False

    def get_path(self, from_row, from_col, to_row, to_col):
        if abs(to_row - from_row) == 2 and from_col == to_col:
            return [(from_row + self._dir, from_col)]
        return []

_PIECE_MAP = {
    "K": King, "R": Rook, "B": Bishop, "N": Knight, "Q": Queen, "P": Pawn
}

def get_piece(token):
    if len(token) == 2 and token[1] in _PIECE_MAP:
        piece = _PIECE_MAP[token[1]]()
        if token[1] == "P":
            piece._dir = -1 if token[0] == "w" else 1
            piece._start_row = None  # set by board context
        return piece
    return None
