from play.entities.pieces import get_piece

class Board:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
        self._pending = []  # list of (from_row, from_col, to_row, to_col)

    def cell(self, row, col):
        return self.grid[row][col]

    def rows(self):
        return len(self.grid)

    def cols(self):
        return len(self.grid[0]) if self.grid else 0

    def request_move(self, from_row, from_col, to_row, to_col):
        self._pending.append((from_row, from_col, to_row, to_col))

    def advance(self, ms):
        for from_row, from_col, to_row, to_col in self._pending:
            token = self.grid[from_row][from_col]
            piece = get_piece(token)
            dest = self.grid[to_row][to_col]
            if not piece or not piece.is_legal_move(from_row, from_col, to_row, to_col, dest=dest):
                continue
            if dest != "." and dest[0] == token[0]:  # same color
                continue
            if any(self.grid[r][c] != "." for r, c in piece.get_path(from_row, from_col, to_row, to_col)):
                continue
            self.grid[from_row][from_col] = "."
            self.grid[to_row][to_col] = token
        self._pending.clear()

    def __str__(self):
        return "\n".join(" ".join(row) for row in self.grid)
