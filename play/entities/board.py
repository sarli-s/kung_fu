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
            piece = self.grid[from_row][from_col]
            self.grid[from_row][from_col] = "."
            self.grid[to_row][to_col] = piece
        self._pending.clear()

    def __str__(self):
        return "\n".join(" ".join(row) for row in self.grid)
