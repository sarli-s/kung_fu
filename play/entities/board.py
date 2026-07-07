from play.entities.pieces import get_piece

MOVE_TIME_PER_CELL = 1000  # ms per cell

class Board:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
        # each entry: (from_row, from_col, to_row, to_col, elapsed_ms)
        self._pending = []

    def cell(self, row, col):
        return self.grid[row][col]

    def rows(self):
        return len(self.grid)

    def cols(self):
        return len(self.grid[0]) if self.grid else 0

    def is_moving(self, row, col):
        return any(fr == row and fc == col for fr, fc, *_ in self._pending)

    def _moving_color(self):
        """Returns the color ('w'/'b') of any piece currently in transit, or None."""
        for fr, fc, *_ in self._pending:
            token = self.grid[fr][fc]
            if token != ".":
                return token[0]
        return None

    def request_move(self, from_row, from_col, to_row, to_col):
        if self.is_moving(from_row, from_col):
            return  # ignore redirect while in transit
        token = self.grid[from_row][from_col]
        moving_color = self._moving_color()
        if moving_color is not None and token != "." and token[0] != moving_color:
            return  # opposite color cannot move while another color is in transit
        self._pending.append((from_row, from_col, to_row, to_col, 0))

    def advance(self, ms):
        still_pending = []
        for from_row, from_col, to_row, to_col, elapsed in self._pending:
            elapsed += ms
            cells = max(abs(to_row - from_row), abs(to_col - from_col))
            if elapsed < cells * MOVE_TIME_PER_CELL:
                still_pending.append((from_row, from_col, to_row, to_col, elapsed))
                continue
            token = self.grid[from_row][from_col]
            piece = get_piece(token)
            dest = self.grid[to_row][to_col]
            if not piece or not piece.is_legal_move(from_row, from_col, to_row, to_col, dest=dest):
                continue
            if dest != "." and dest[0] == token[0]:
                continue
            if any(self.grid[r][c] != "." for r, c in piece.get_path(from_row, from_col, to_row, to_col)):
                continue
            self.grid[from_row][from_col] = "."
            self.grid[to_row][to_col] = token
        self._pending = still_pending

    def __str__(self):
        return "\n".join(" ".join(row) for row in self.grid)
