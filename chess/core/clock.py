from chess.entities.jump import JumpCommand
from chess.entities.move_command import MoveCommand


class RealTimeArbiter:
    def __init__(self, config):
        self._config = config
        self._pending = []   # active MoveCommands (board not yet mutated)
        self._airborne = []

    def add_move(self, cmd: MoveCommand):
        self._pending.append(cmd)

    def add_jump(self, cmd: JumpCommand):
        self._airborne.append(cmd)

    def is_moving(self, row, col):
        return any(cmd.from_row == row and cmd.from_col == col for cmd in self._pending)

    def is_airborne(self, row, col):
        return any(cmd.row == row and cmd.col == col for cmd in self._airborne)

    def get_airborne_at(self, row, col):
        return next((j for j in self._airborne if j.row == row and j.col == col), None)

    def inflight_positions(self, cmd):
        return {(c.current_row, c.current_col) for c in self._pending if c is not cmd}

    def advance(self, ms, resolve_checkpoint_fn):
        for cmd in self._pending:
            cmd.elapsed += ms

        # collect all checkpoints due this tick across all moves, preserve FIFO registration order
        due = sorted(
            [(cmd, due_time, r, c)
             for cmd in self._pending
             for (due_time, r, c) in cmd.checkpoints
             if due_time <= cmd.elapsed],
            key=lambda x: (x[1], self._pending.index(x[0]))
        )

        resolved = set()
        for cmd, due_time, r, c in due:
            if id(cmd) in resolved:
                continue
            finished = resolve_checkpoint_fn(cmd, r, c)
            if finished:
                resolved.add(id(cmd))

        self._pending = [cmd for cmd in self._pending if id(cmd) not in resolved]
        self._tick_airborne(ms)

    def _tick_airborne(self, ms):
        self._airborne = [j for j in self._airborne if j.remaining > ms]
        for j in self._airborne:
            j.remaining -= ms
