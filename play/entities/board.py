from play.entities.pieces import PieceFactory
from play.entities.rules import BoardRules, ChessBoardRules
from play.utils.token_format import TextTokenFormat
from play.utils.event_emitter import EventEmitter
from play.entities.game_commands import MoveCommand, JumpCommand
from play.config import ChessConfig


class Board(EventEmitter):
    def __init__(self, grid, piece_factory=None, token_format=None, rules=None, config=None):
        EventEmitter.__init__(self)
        self._fmt = token_format or TextTokenFormat()
        self._piece_factory = piece_factory or PieceFactory()
        self._rules = rules or ChessBoardRules()
        self._config = config or ChessConfig
        self._grid = [[self._fmt.encode(cell) for cell in row] for row in grid]
        self._pending = []
        self._airborne = []
        self.game_over = False

    # ── Public read interface ──────────────────────────────────────────────────

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

    def is_moving(self, row, col):
        return any(cmd.from_row == row and cmd.from_col == col for cmd in self._pending)

    def is_airborne(self, row, col):
        return any(cmd.row == row and cmd.col == col for cmd in self._airborne)

    # ── Requests ───────────────────────────────────────────────────────────────

    def request_jump(self, row, col):
        if self._grid[row][col] == self._fmt.empty():
            return
        if self.is_moving(row, col) or self.is_airborne(row, col):
            return
        self._airborne.append(JumpCommand(row, col, self._config.jump_duration))

    def request_move(self, from_row, from_col, to_row, to_col):
        if self.is_moving(from_row, from_col):
            return
        token = self._grid[from_row][from_col]
        moving_color = self._moving_color()
        if moving_color is not None and token != self._fmt.empty() and self._fmt.color(token) != moving_color:
            return
        self._pending.append(MoveCommand(from_row, from_col, to_row, to_col))

    # ── Advance ────────────────────────────────────────────────────────────────

    def advance(self, ms):
        self._pending = [cmd for cmd in self._pending if not self._try_resolve(cmd, ms)]
        self._tick_airborne(ms)

    def _try_resolve(self, cmd, ms):
        """Returns True if the command should be removed from pending."""
        cmd.elapsed += ms
        cells = max(abs(cmd.to_row - cmd.from_row), abs(cmd.to_col - cmd.from_col))
        if cmd.elapsed < (cells - 1) * self._config.move_time_per_cell:
            return False
        return self._execute_move(cmd)

    def _execute_move(self, cmd):
        """Validates and applies a move. Returns True to remove from pending."""
        empty = self._fmt.empty()
        token = self._grid[cmd.from_row][cmd.from_col]
        dest = self._grid[cmd.to_row][cmd.to_col]
        dest_text = self._fmt.decode(dest)

        piece = self._piece_factory(self._fmt.decode(token))
        if piece:
            self._rules.prepare_piece(token, piece, self, self._fmt)

        if not piece or not piece.is_legal_move(cmd, dest=dest_text):
            return True
        if dest != empty and self._fmt.color(dest) == self._fmt.color(token):
            return True
        if any(self._grid[r][c] != empty for r, c in piece.get_path(cmd)):
            return True
        if self._captured_by_airborne(cmd, token):
            return True

        self._apply_move(cmd, token, dest, dest_text)
        return True

    def _captured_by_airborne(self, cmd, token):
        """If an airborne enemy occupies the destination, consume the attacker and return True."""
        airborne_cmd = next((j for j in self._airborne if j.row == cmd.to_row and j.col == cmd.to_col), None)
        if airborne_cmd is None:
            return False
        airborne_token = self._grid[cmd.to_row][cmd.to_col]
        empty = self._fmt.empty()
        if airborne_token != empty and self._fmt.color(airborne_token) != self._fmt.color(token):
            self._grid[cmd.from_row][cmd.from_col] = empty
            return True
        return False

    def _apply_move(self, cmd, token, dest, dest_text):
        empty = self._fmt.empty()
        self._grid[cmd.from_row][cmd.from_col] = empty
        if dest != empty and self._rules.is_royal(dest, self._fmt):
            self.game_over = True
            self.emit("on_game_over", winner=self._fmt.color(token))
        elif dest != empty:
            self.emit("on_capture", captured=dest_text, by=self._fmt.decode(token), row=cmd.to_row, col=cmd.to_col)
        promoted = self._rules.get_promotion(token, cmd.to_row, self, self._fmt)
        arrival = promoted or token
        if promoted:
            self.emit("on_promotion", piece=self._fmt.decode(arrival), row=cmd.to_row, col=cmd.to_col)
        self._grid[cmd.to_row][cmd.to_col] = arrival

    def _tick_airborne(self, ms):
        self._airborne = [j for j in self._airborne if j.remaining > ms]
        for j in self._airborne:
            j.remaining -= ms

    # ── Internals ──────────────────────────────────────────────────────────────

    def _moving_color(self):
        for cmd in self._pending:
            token = self._grid[cmd.from_row][cmd.from_col]
            if token != self._fmt.empty():
                return self._fmt.color(token)
        return None

    def __str__(self):
        return "\n".join(" ".join(self._fmt.decode(cell) for cell in row) for row in self._grid)
