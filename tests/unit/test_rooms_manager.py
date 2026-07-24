"""Tests for RoomsManager (stage 2c)."""

import pytest
from server.game.rooms_manager import RoomsManager


class TestRoomsManager:
    def test_default_room_created_on_init(self):
        """Default room is created when RoomsManager is initialized."""
        manager = RoomsManager()
        assert manager.room_exists("default")
        assert manager.get_default_room() is not None

    def test_get_room_returns_engine(self):
        """get_room returns the GameEngine for a room."""
        manager = RoomsManager()
        engine = manager.get_room("default")
        assert engine is not None
        assert hasattr(engine, "advance")
        assert hasattr(engine, "cell")

    def test_list_rooms_includes_default(self):
        """list_rooms includes the default room."""
        manager = RoomsManager()
        rooms = manager.list_rooms()
        assert "default" in rooms
        assert len(rooms) == 1

    def test_create_room_with_auto_id(self):
        """create_room generates a room ID if not provided."""
        manager = RoomsManager()
        room_id = manager.create_room()
        
        assert room_id is not None
        assert len(room_id) == 8  # Short UUID
        assert manager.room_exists(room_id)
        assert manager.get_room(room_id) is not None

    def test_create_room_with_custom_id(self):
        """create_room accepts a custom room ID."""
        manager = RoomsManager()
        room_id = manager.create_room("custom_room")
        
        assert room_id == "custom_room"
        assert manager.room_exists("custom_room")

    def test_create_room_duplicate_raises_error(self):
        """create_room raises error if room ID already exists."""
        manager = RoomsManager()
        manager.create_room("test_room")
        
        with pytest.raises(ValueError, match="already exists"):
            manager.create_room("test_room")

    def test_delete_room_removes_room(self):
        """delete_room removes a room."""
        manager = RoomsManager()
        room_id = manager.create_room("to_delete")
        
        assert manager.room_exists("to_delete")
        manager.delete_room("to_delete")
        assert not manager.room_exists("to_delete")

    def test_delete_default_room_raises_error(self):
        """delete_room raises error when trying to delete default room."""
        manager = RoomsManager()
        
        with pytest.raises(ValueError, match="Cannot delete the default room"):
            manager.delete_room("default")

    def test_delete_nonexistent_room_raises_error(self):
        """delete_room raises error if room doesn't exist."""
        manager = RoomsManager()
        
        with pytest.raises(ValueError, match="does not exist"):
            manager.delete_room("nonexistent")

    def test_multiple_rooms_have_independent_engines(self):
        """Each room has its own independent GameEngine."""
        manager = RoomsManager()
        room1_id = manager.create_room("room1")
        room2_id = manager.create_room("room2")
        
        engine1 = manager.get_room(room1_id)
        engine2 = manager.get_room(room2_id)
        
        # Engines should be different objects
        assert engine1 is not engine2
        
        # Advancing one shouldn't affect the other
        engine1.advance(100)
        # Both should still be valid
        assert engine1 is not None
        assert engine2 is not None

    def test_room_engines_have_correct_starting_position(self):
        """Each room's engine has the correct starting chess position."""
        manager = RoomsManager()
        engine = manager.get_default_room()
        
        # Check piece count
        piece_count = 0
        for row in range(engine.rows()):
            for col in range(engine.cols()):
                cell = engine.cell(row, col)
                if cell != ".":
                    piece_count += 1
        
        assert piece_count == 32  # 16 white + 16 black pieces
