"""Tests for GameBus event subscription and exception handling."""

import pytest
from chess.services.board_builder import build_board
from server.game.game_bus import GameBus


@pytest.fixture
def engine():
    """Create a simple test engine."""
    board_lines = [
        "bR bN bB bQ bK bB bN bR",
        "bP bP bP bP bP bP bP bP",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        "wP wP wP wP wP wP wP wP",
        "wR wN wB wK wQ wB wN wR",
    ]
    return build_board(board_lines)


@pytest.fixture
def bus(engine):
    """Create a GameBus for the engine."""
    return GameBus(engine)


class TestGameBusSubscribe:
    def test_subscribe_registers_listener(self, bus):
        """Listener is registered and can be called."""
        called = []
        bus.subscribe("on_move", "test_listener", lambda **data: called.append(data))
        
        # Trigger a move (pawn moves 2 cells = 2000ms)
        bus.engine.request_move(6, 4, 4, 4)  # white pawn e2 -> e4
        bus.engine.advance(2000)
        
        assert len(called) == 1
        assert called[0]["piece"] == "wP"

    def test_multiple_listeners_same_event(self, bus):
        """Multiple listeners for same event all get called."""
        calls1 = []
        calls2 = []
        bus.subscribe("on_move", "listener1", lambda **data: calls1.append(data))
        bus.subscribe("on_move", "listener2", lambda **data: calls2.append(data))
        
        bus.engine.request_move(6, 4, 4, 4)
        bus.engine.advance(2000)
        
        assert len(calls1) == 1
        assert len(calls2) == 1

    def test_exception_in_listener_does_not_break_chain(self, bus, capsys):
        """If one listener throws, others still get called."""
        calls = []
        
        def failing_listener(**data):
            raise ValueError("Intentional error")
        
        def working_listener(**data):
            calls.append(data)
        
        bus.subscribe("on_move", "failing", failing_listener)
        bus.subscribe("on_move", "working", working_listener)
        
        bus.engine.request_move(6, 4, 4, 4)
        bus.engine.advance(2000)
        
        # Working listener should still be called
        assert len(calls) == 1
        # Error should be logged
        captured = capsys.readouterr()
        assert "Error in listener 'failing'" in captured.out

    def test_subscribe_to_capture_event(self, bus):
        """Capture event is broadcast to listeners."""
        captures = []
        bus.subscribe("on_capture", "capture_logger", lambda **data: captures.append(data))
        
        # Move white pawn to capture position
        bus.engine.request_move(6, 4, 4, 4)  # e2 -> e4
        bus.engine.advance(2000)
        
        # Move black pawn to be captured
        bus.engine.request_move(1, 3, 3, 3)  # d7 -> d5
        bus.engine.advance(2000)
        
        # Move white pawn to capture
        bus.engine.request_move(4, 4, 3, 3)  # e4 -> d5 (capture)
        bus.engine.advance(2000)
        
        assert len(captures) == 1
        assert captures[0]["captured"] == "bP"

    def test_subscribe_to_game_over_event(self, bus):
        """Game over event is broadcast to listeners."""
        game_overs = []
        bus.subscribe("on_game_over", "game_over_logger", lambda **data: game_overs.append(data))
        
        # No game over yet
        assert len(game_overs) == 0
