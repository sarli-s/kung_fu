import time
from chess.entities.move_command import MoveCommand
from chess.entities.jump import JumpCommand
from chess.entities.pieces.factory import PieceFactory
from chess.rules.engine_rules import ChessBoardRules
from chess.core.clock import RealTimeArbiter
from chess.core.move_tracker import MoveTracker
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
        self.start_time = time.time()
        self._pawn_start_rows = self._record_pawn_starts()
        self.move_tracker = MoveTracker()
        self.subscribe("on_move", self.move_tracker.on_move)
        self.subscribe("on_capture", self._on_capture_event)

    def _record_pawn_starts(self):
        starts = {}
        fmt = self._fmt
        for r in range(self._board.rows()):
            for c in range(self._board.cols()):
                token = self._board.get_raw(r, c)
                if token != fmt.empty() and fmt.piece_type(token) == "P":
                    starts[(r, c)] = r
        return starts

    def _on_capture_event(self, row, col, by=None, captured=None, **_):
        self.move_tracker.mark_capture(row, col, capturing_piece=by, captured_piece=captured)

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

    def is_short_rest(self, row, col):
        return self._clock.is_short_rest(row, col)

    def is_long_rest(self, row, col):
        return self._clock.is_long_rest(row, col)

    def get_move_command(self, row, col):
        for cmd in self._clock._pending:
            if cmd.from_row == row and cmd.from_col == col:
                return cmd
        return None

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
        if self._clock.is_short_rest(from_row, from_col) or self._clock.is_long_rest(from_row, from_col):
            return
        token = self._board.get_raw(from_row, from_col)
        if token == self._fmt.empty():
            return
        # Prevents position swaps between two pieces moving simultaneously
        for other_cmd in self._clock._pending:
            if other_cmd.to_row == from_row and other_cmd.to_col == from_col:
                return
        piece = self._piece_factory(self._fmt.decode(token))
        if not piece:
            return
        start_row = self._pawn_start_rows.get((from_row, from_col))
        self._rules.prepare_piece(token, piece, self._board, self._fmt, from_row=start_row)
        move = MoveCommand(from_row, from_col, to_row, to_col)
        dest_empty = self._board.is_empty(to_row, to_col)  # pawn diagonal capture legality is fixed at request time, not at arrival
        if not piece.is_legal_move(move, dest_empty=dest_empty):
            return
        t = self._config.move_time_per_cell
        path = piece.get_path(move)
        full_path = path + [(to_row, to_col)]
        move.from_token = token
        move.checkpoints = [(k * t, r, c) for k, (r, c) in enumerate(full_path, start=1)]
        self._clock.add_move(move)

    # ── Advance ────────────────────────────────────────────────────────────────

    def advance(self, ms):
        expired_jumps = [j for j in self._clock._airborne if j.remaining <= ms]
        self._clock.advance(ms, self._resolve_checkpoint)
        for j in expired_jumps:
            self._clock.add_short_rest(j.row, j.col, self._config.rest_after_jump)

    def _resolve_checkpoint(self, cmd, r, c):
        fmt = self._fmt
        empty = fmt.empty()
        token = cmd.from_token
        is_target = (r == cmd.to_row and c == cmd.to_col)
        cell_content = self._board.get_raw(r, c)
        inflight = self._clock.inflight_positions(cmd)
        occupied = cell_content != empty or (r, c) in inflight

        if not is_target:
            if occupied:
                # Head-on collision: let both pieces pass so neither is unfairly blocked mid-path.
                if self._get_enemy_moving_to_target(cmd, cmd.to_row, cmd.to_col, fmt):
                    cmd.current_row, cmd.current_col = r, c
                    return False
                prev = self._prev_cell(cmd, r, c)
                self._land(cmd, token, prev[0], prev[1])
                return True
            cmd.current_row, cmd.current_col = r, c
            return False

        # target cell
        if self._captured_by_airborne(cmd, token):
            return True
        if occupied and cell_content != empty and fmt.color(cell_content) == fmt.color(token):
            prev = self._prev_cell(cmd, r, c)
            self._land(cmd, token, prev[0], prev[1])
            return True
        if (r, c) in inflight and cell_content == empty:
            enemy_cmd = self._get_enemy_moving_to_target(cmd, r, c, fmt)
            if enemy_cmd:
                # First arrival wins the contested cell — captures the in-flight enemy.
                cmd.current_row, cmd.current_col = r, c
                self._land(cmd, token, r, c)
                return True
            # The cell is logically reserved by an in-flight friendly — landing here would cause overlap.
            prev = self._prev_cell(cmd, r, c)
            self._land(cmd, token, prev[0], prev[1])
            return True
        cmd.current_row, cmd.current_col = r, c
        self._land(cmd, token, r, c)
        return True

    def _prev_cell(self, cmd, r, c):
        full_path = [p for _, p_r, p_c in cmd.checkpoints for p in [(p_r, p_c)]]
        idx = full_path.index((r, c))
        return full_path[idx - 1] if idx > 0 else (cmd.from_row, cmd.from_col)

    def _land(self, cmd, token, to_row, to_col):
        fmt = self._fmt
        empty = fmt.empty()
        dest = self._board.get_raw(to_row, to_col)
        dest_text = fmt.decode(dest)
        self._board.set_raw(cmd.from_row, cmd.from_col, empty)
        self.emit("on_move", piece=fmt.decode(token), from_row=cmd.from_row, from_col=cmd.from_col, to_row=to_row, to_col=to_col)
        king_captured = dest != empty and self._rules.is_royal(dest, fmt)
        if king_captured:
            self.game_over = True
            self.emit("on_game_over", winner=fmt.color(token))
        elif dest != empty:
            self.emit("on_capture", captured=dest_text, by=fmt.decode(token), row=to_row, col=to_col)
        promoted = None if king_captured else self._rules.get_promotion(token, to_row, self._board, fmt)
        arrival = promoted or token
        if promoted:
            self.emit("on_promotion", piece=fmt.decode(arrival), row=to_row, col=to_col)
        self._board.set_raw(to_row, to_col, arrival)
        self._clock.add_long_rest(to_row, to_col, self._config.rest_after_move)

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

    def _get_enemy_moving_to_target(self, cmd, target_row, target_col, fmt):
        for other_cmd in self._clock._pending:
            if other_cmd is cmd:
                continue
            if other_cmd.to_row == target_row and other_cmd.to_col == target_col:
                other_token = other_cmd.from_token
                if fmt.color(other_token) != fmt.color(cmd.from_token):
                    return other_cmd
        return None

    def __str__(self):
        return str(self._board)
