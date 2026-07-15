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
        cmd.checkpoints = [(1000, 1, 1)]
        self.arbiter.add_move(cmd)
        resolve_called = []

        def resolve(c, r, col):
            resolve_called.append((c, r, col))
            return True

        self.arbiter.advance(1000, resolve)
        assert len(resolve_called) == 1
        assert resolve_called[0][0] is cmd
        assert resolve_called[0][1] == 1
        assert resolve_called[0][2] == 1

    def test_advance_reduces_airborne_duration(self):
        self.arbiter.add_jump(JumpCommand(0, 0, 1000))
        self.arbiter.advance(300, lambda c, r, col: False)
        assert self.arbiter.get_airborne_at(0, 0).remaining == 700

    # ── wait-invariant ─────────────────────────────────────────────────────────

    def test_wait_invariant_single_vs_multiple_waits(self):
        """Same command sequence must produce identical board state whether done
        via one large wait or several smaller waits summing to the same total."""
        from chess.services.board_builder import build_board
        from chess.core.controller import handle_commands

        # Scenario: rook moves 2 cells, pawn moves 1 cell, both start simultaneously
        board_lines = ["wR . . bP"]

        # Path 1: one large wait
        engine1 = build_board(board_lines)
        handle_commands(engine1, [
            "click 50 50", "click 250 50",      # wR: (0,0) -> (0,2)
            "click 350 50", "click 50 50",      # bP: (0,3) -> (0,0)
            "wait 2000"
        ])
        state1 = str(engine1)

        # Path 2: multiple smaller waits summing to 2000
        engine2 = build_board(board_lines)
        handle_commands(engine2, [
            "click 50 50", "click 250 50",      # wR: (0,0) -> (0,2)
            "click 350 50", "click 50 50",      # bP: (0,3) -> (0,0)
            "wait 500", "wait 500", "wait 500", "wait 500"
        ])
        state2 = str(engine2)

        assert state1 == state2
