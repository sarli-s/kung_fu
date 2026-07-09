from chess.utils.token_format import TextTokenFormat


class Board:
    def __init__(self, grid, token_format=None, config=None):
        self._fmt = token_format or TextTokenFormat()
        self._grid = [[self._fmt.encode(cell) for cell in row] for row in grid]

    def cell(self, row, col):
        return self._fmt.decode(self._grid[row][col])

    def rows(self):
        return len(self._grid)

    def cols(self):
        return len(self._grid[0]) if self._grid else 0

    def is_empty(self, row, col):
        return self._grid[row][col] == self._fmt.empty()

    def same_color(self, row1, col1, row2, col2):
        return self._fmt.color(self._grid[row1][col1]) == self._fmt.color(self._grid[row2][col2])

    def get_raw(self, row, col):
        return self._grid[row][col]

    def set_raw(self, row, col, value):
        self._grid[row][col] = value

    def fmt(self):
        return self._fmt

    def __str__(self):
        return "\n".join(" ".join(self._fmt.decode(cell) for cell in row) for row in self._grid)
