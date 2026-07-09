from chess.entities.jump import JumpCommand
from chess.entities.move_command import MoveCommand


class RealTimeArbiter:
    def __init__(self, config):
        self._config = config
        self._pending = []
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

    def advance(self, ms, resolve_fn):
        self._pending = [cmd for cmd in self._pending if not resolve_fn(cmd, ms)]
        self._tick_airborne(ms)

    def _tick_airborne(self, ms):
        self._airborne = [j for j in self._airborne if j.remaining > ms]
        for j in self._airborne:
            j.remaining -= ms

    def moving_color(self, grid, fmt):
        for cmd in self._pending:
            token = grid[cmd.from_row][cmd.from_col]
            if token != fmt.empty():
                return fmt.color(token)
        return None
