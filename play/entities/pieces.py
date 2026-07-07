class Piece:
    def is_legal_move(self, from_row, from_col, to_row, to_col):
        raise NotImplementedError

    def get_path(self, from_row, from_col, to_row, to_col):
        """Returns list of intermediate (row, col) squares (excludes start and end)."""
        return []

class King(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col):
        return max(abs(to_row - from_row), abs(to_col - from_col)) == 1

class Rook(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col):
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
    def is_legal_move(self, from_row, from_col, to_row, to_col):
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
    def is_legal_move(self, from_row, from_col, to_row, to_col):
        dr, dc = abs(to_row - from_row), abs(to_col - from_col)
        return sorted([dr, dc]) == [1, 2]

class Queen(Piece):
    def is_legal_move(self, from_row, from_col, to_row, to_col):
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

_PIECE_MAP = {
    "K": King, "R": Rook, "B": Bishop, "N": Knight, "Q": Queen
}

def get_piece(token):
    if len(token) == 2 and token[1] in _PIECE_MAP:
        return _PIECE_MAP[token[1]]()
    return None
