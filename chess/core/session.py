from chess.entities.move_command import MoveCommand
from chess.entities.jump import JumpCommand
from chess.entities.pieces.factory import PieceFactory
from chess.rules.game_rules import ChessBoardRules
from chess.core.clock import RealTimeArbiter
from chess.utils.event_emitter import EventEmitter
from chess.config import ChessConfig


class GameEngine(EventEmitter):
    def __init__(self, board, piece_factory=None, rules=None, config=None):
        EventEmitter.__init__(self)
        self._board = board
        self._fmt = board.fmt()
        self._piece_factory = piece_factory or PieceFactory()
        self._rules = rules or ChessBoardRules()
        self._config = config or ChessConfig
        self._clock = RealTimeArbiter(self._config)
        self.game_over = False

    # ── Public read interface (delegates to board/clock) ───────────────────────

    def cell(self, row, col):
        return self._board.cell(row, col)

    def rows(self):
        return self._board.rows()

    def cols(self):
        return self._board.cols()

    def is_empty(self, row, col):
        return self._board.is_empty(row, col)

    def same_color(self, row1, col1, row2, col2):
        return self._board.same_color(row1, col1, row2, col2)

    def is_moving(self, row, col):
        return self._clock.is_moving(row, col)

    def is_airborne(self, row, col):
        return self._clock.is_airborne(row, col)

    # ── Requests ───────────────────────────────────────────────────────────────

    def request_jump(self, row, col):
        if self._board.is_empty(row, col):
            return
        if self._clock.is_moving(row, col) or self._clock.is_airborne(row, col):
            return
        self._clock.add_jump(JumpCommand(row, col, self._config.jump_duration))

    def request_move(self, from_row, from_col, to_row, to_col):
        if self._clock.is_moving(from_row, from_col):
            return
        token = self._board.get_raw(from_row, from_col)
        moving_color = self._clock.moving_color(self._board._grid, self._fmt)
        if moving_color is not None and token != self._fmt.empty() and self._fmt.color(token) != moving_color:
            return
        self._clock.add_move(MoveCommand(from_row, from_col, to_row, to_col))

    # ── Advance ────────────────────────────────────────────────────────────────

    def advance(self, ms):
        self._clock.advance(ms, self._try_resolve)

    def _try_resolve(self, cmd, ms):
        cmd.elapsed += ms
        cells = max(abs(cmd.to_row - cmd.from_row), abs(cmd.to_col - cmd.from_col))
        if cmd.elapsed < (cells) * self._config.move_time_per_cell:
            return False
        return self._execute_move(cmd)

    def _execute_move(self, cmd):
        fmt = self._fmt
        empty = fmt.empty()
        token = self._board.get_raw(cmd.from_row, cmd.from_col)
        dest = self._board.get_raw(cmd.to_row, cmd.to_col)
        dest_text = fmt.decode(dest)

        piece = self._piece_factory(fmt.decode(token))
        if piece:
            self._rules.prepare_piece(token, piece, self._board, fmt)

        if not piece or not piece.is_legal_move(cmd, dest_empty=self._board.is_empty(cmd.to_row, cmd.to_col)):
            return True
        if dest != empty and fmt.color(dest) == fmt.color(token):
            return True
        if any(self._board.get_raw(r, c) != empty for r, c in piece.get_path(cmd)):
            return True
        if self._captured_by_airborne(cmd, token):
            return True

        self._apply_move(cmd, token, dest, dest_text)
        return True

    def _captured_by_airborne(self, cmd, token):
        airborne_cmd = self._clock.get_airborne_at(cmd.to_row, cmd.to_col)
        if airborne_cmd is None:
            return False
        airborne_token = self._board.get_raw(cmd.to_row, cmd.to_col)
        empty = self._fmt.empty()
        if airborne_token != empty and self._fmt.color(airborne_token) != self._fmt.color(token):
            self._board.set_raw(cmd.from_row, cmd.from_col, empty)
            return True
        return False

    def _apply_move(self, cmd, token, dest, dest_text):
        fmt = self._fmt
        empty = fmt.empty()
        self._board.set_raw(cmd.from_row, cmd.from_col, empty)
        if dest != empty and self._rules.is_royal(dest, fmt):
            self.game_over = True
            self.emit("on_game_over", winner=fmt.color(token))
        elif dest != empty:
            self.emit("on_capture", captured=dest_text, by=fmt.decode(token), row=cmd.to_row, col=cmd.to_col)
        promoted = self._rules.get_promotion(token, cmd.to_row, self._board, fmt)
        arrival = promoted or token
        if promoted:
            self.emit("on_promotion", piece=fmt.decode(arrival), row=cmd.to_row, col=cmd.to_col)
        self._board.set_raw(cmd.to_row, cmd.to_col, arrival)

    def __str__(self):
        return str(self._board)
