import pytest
from chess.core.clock import RealTimeArbiter
from chess.entities.move_command import MoveCommand
from chess.entities.jump import JumpCommand
from chess.config import ChessConfig


class TestRealTimeArbiter:
    def setup_method(self):
        self.arbiter = RealTimeArbiter(ChessConfig)

    # ── add_move ───────────────────────────────────────────────────────────────

    def test_add_move_adds_to_pending(self):
        cmd = MoveCommand(0, 0, 1, 1)
        self.arbiter.add_move(cmd)
        assert self.arbiter.is_moving(0, 0) is True

    # ── add_jump ───────────────────────────────────────────────────────────────

    def test_add_jump_adds_to_airborne(self):
        cmd = JumpCommand(0, 0, 1000)
        self.arbiter.add_jump(cmd)
        assert self.arbiter.is_airborne(0, 0) is True

    # ── is_moving ──────────────────────────────────────────────────────────────

    def test_is_moving_true_for_pending(self):
        self.arbiter.add_move(MoveCommand(0, 0, 1, 1))
        assert self.arbiter.is_moving(0, 0) is True

    def test_is_moving_false_for_non_pending(self):
        assert self.arbiter.is_moving(0, 0) is False

    def test_is_moving_false_after_advance_resolves(self):
        cmd = MoveCommand(0, 0, 1, 1)
        self.arbiter.add_move(cmd)
        self.arbiter.advance(2000, lambda c, m: True)
        assert self.arbiter.is_moving(0, 0) is False

    # ── is_airborne ────────────────────────────────────────────────────────────

    def test_is_airborne_true_for_airborne(self):
        self.arbiter.add_jump(JumpCommand(0, 0, 1000))
        assert self.arbiter.is_airborne(0, 0) is True

    def test_is_airborne_false_for_non_airborne(self):
        assert self.arbiter.is_airborne(0, 0) is False

    def test_is_airborne_false_after_duration_expires(self):
        self.arbiter.add_jump(JumpCommand(0, 0, 500))
        self.arbiter._tick_airborne(1000)
        assert self.arbiter.is_airborne(0, 0) is False

    # ── get_airborne_at ────────────────────────────────────────────────────────

    def test_get_airborne_at_returns_command(self):
        cmd = JumpCommand(1, 2, 1000)
        self.arbiter.add_jump(cmd)
        assert self.arbiter.get_airborne_at(1, 2) is cmd

    def test_get_airborne_at_returns_none_if_not_found(self):
        assert self.arbiter.get_airborne_at(0, 0) is None

    # ── advance ────────────────────────────────────────────────────────────────

    def test_advance_resolves_pending_commands(self):
        cmd = MoveCommand(0, 0, 1, 1)
        cmd.elapsed = 0
        self.arbiter.add_move(cmd)
        resolve_called = []

        def resolve(c, m):
            resolve_called.append((c, m))
            return True

        self.arbiter.advance(100, resolve)
        assert len(resolve_called) == 1
        assert resolve_called[0][0] is cmd
        assert resolve_called[0][1] == 100

    def test_advance_reduces_airborne_duration(self):
        self.arbiter.add_jump(JumpCommand(0, 0, 1000))
        self.arbiter.advance(300, lambda c, m: False)
        assert self.arbiter.get_airborne_at(0, 0).remaining == 700

    # ── moving_color ───────────────────────────────────────────────────────────

    def test_moving_color_returns_color_of_moving_piece(self):
        grid = [["wR", ".", "."], [".", ".", "."], [".", ".", "."]]
        self.arbiter.add_move(MoveCommand(0, 0, 0, 2))
        from chess.utils.token_format import TextTokenFormat
        fmt = TextTokenFormat()
        assert self.arbiter.moving_color(grid, fmt) == "w"

    def test_moving_color_returns_none_if_no_moving_piece(self):
        grid = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
        from chess.utils.token_format import TextTokenFormat
        fmt = TextTokenFormat()
        assert self.arbiter.moving_color(grid, fmt) is None

    def test_moving_color_returns_none_if_empty_cell(self):
        grid = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
        self.arbiter.add_move(MoveCommand(0, 0, 0, 2))
        from chess.utils.token_format import TextTokenFormat
        fmt = TextTokenFormat()
        assert self.arbiter.moving_color(grid, fmt) is None
