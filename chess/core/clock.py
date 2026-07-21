from chess.entities.jump import JumpCommand
from chess.entities.move_command import MoveCommand


class RealTimeArbiter:
    def __init__(self, config):
        self._config = config
        self._pending = []
        self._airborne = []
        self._short_rest = {}  # {(row, col): remaining_ms}
        self._long_rest = {}   # {(row, col): remaining_ms}

    def add_move(self, cmd: MoveCommand):
        self._pending.append(cmd)

    def add_jump(self, cmd: JumpCommand):
        self._airborne.append(cmd)

    def is_moving(self, row, col):
        return any(cmd.from_row == row and cmd.from_col == col for cmd in self._pending)

    def is_airborne(self, row, col):
        return any(cmd.row == row and cmd.col == col for cmd in self._airborne)

    def add_short_rest(self, row, col, ms):
        self._short_rest[(row, col)] = ms

    def add_long_rest(self, row, col, ms):
        self._long_rest[(row, col)] = ms

    def is_short_rest(self, row, col):
        return (row, col) in self._short_rest

    def is_long_rest(self, row, col):
        return (row, col) in self._long_rest

    def get_airborne_at(self, row, col):
        return next((j for j in self._airborne if j.row == row and j.col == col), None)

    def inflight_positions(self, cmd):
        return {(c.current_row, c.current_col) for c in self._pending if c is not cmd}

    def advance(self, ms, resolve_checkpoint_fn):
        for cmd in self._pending:
            cmd.elapsed += ms
            if not hasattr(cmd, "next_idx"):
                cmd.next_idx = 0

        due = []
        for cmd in self._pending:
            while cmd.next_idx < len(cmd.checkpoints) and cmd.checkpoints[cmd.next_idx][0] <= cmd.elapsed:
                due_time, r, c = cmd.checkpoints[cmd.next_idx]
                due.append((cmd, due_time, r, c))
                cmd.next_idx += 1

        due.sort(key=lambda x: (x[1], self._pending.index(x[0])))

        resolved = set()
        for cmd, due_time, r, c in due:
            if id(cmd) in resolved:
                continue
            finished = resolve_checkpoint_fn(cmd, r, c)
            if finished:
                resolved.add(id(cmd))

        self._pending = [cmd for cmd in self._pending if id(cmd) not in resolved]
        self._tick_airborne(ms)
        self._tick_rests(ms)
    

    def _tick_airborne(self, ms):
        self._airborne = [j for j in self._airborne if j.remaining > ms]
        for j in self._airborne:
            j.remaining -= ms

    def _tick_rests(self, ms):
        for d in (self._short_rest, self._long_rest):
            expired = [k for k, v in d.items() if v <= ms]
            for k in expired:
                del d[k]
            for k in d:
                d[k] -= ms
