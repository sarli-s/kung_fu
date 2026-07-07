from play.entities.pieces import get_piece

MOVE_TIME_PER_CELL = 1000  # ms per cell
JUMP_DURATION = 1000  # ms

class Board:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
        # each entry: (from_row, from_col, to_row, to_col, elapsed_ms)
        self._pending = []
        # airborne: {(row, col): remaining_ms}
        self._airborne = {}
        self.game_over = False

    def cell(self, row, col):
        return self.grid[row][col]

    def rows(self):
        return len(self.grid)

    def cols(self):
        return len(self.grid[0]) if self.grid else 0

    def is_moving(self, row, col):
        return any(fr == row and fc == col for fr, fc, *_ in self._pending)

    def is_airborne(self, row, col):
        return (row, col) in self._airborne

    def request_jump(self, row, col):
        token = self.grid[row][col]
        if token == ".":
            return
        if self.is_moving(row, col):
            return
        if self.is_airborne(row, col):
            return
        self._airborne[(row, col)] = JUMP_DURATION

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
            if elapsed < (cells - 1) * MOVE_TIME_PER_CELL:
                still_pending.append((from_row, from_col, to_row, to_col, elapsed))
                continue
            token = self.grid[from_row][from_col]
            piece = get_piece(token)
            dest = self.grid[to_row][to_col]
            if piece and token[1] == "P":
                piece._start_row = (self.rows() - 1) if token[0] == "w" else 0
            if not piece or not piece.is_legal_move(from_row, from_col, to_row, to_col, dest=dest):
                continue
            if dest != "." and dest[0] == token[0]:
                continue
            if any(self.grid[r][c] != "." for r, c in piece.get_path(from_row, from_col, to_row, to_col)):
                continue
            # airborne capture: if destination has an airborne enemy, it captures the mover
            if (to_row, to_col) in self._airborne:
                airborne_token = self.grid[to_row][to_col]
                if airborne_token != "." and airborne_token[0] != token[0]:
                    # airborne piece captures the arriving mover — mover is removed
                    self.grid[from_row][from_col] = "."
                    continue
            self.grid[from_row][from_col] = "."
            if dest != "." and dest[1] == "K":
                self.game_over = True
            arrival = token
            if token[1] == "P":
                last_row = 0 if token[0] == "w" else self.rows() - 1
                if to_row == last_row:
                    arrival = token[0] + "Q"
            self.grid[to_row][to_col] = arrival
        self._pending = still_pending

        # tick down airborne timers after processing arrivals
        expired = [cell for cell, rem in self._airborne.items() if rem <= ms]
        for cell in expired:
            del self._airborne[cell]
        for cell in list(self._airborne):
            self._airborne[cell] -= ms

    def __str__(self):
        return "\n".join(" ".join(row) for row in self.grid)
