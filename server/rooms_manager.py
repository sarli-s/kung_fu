"""
Rooms manager for multi-engine support.

Structured to support future room creation/join logic (stage 6).
"""

import uuid
from chess.services.board_builder import build_board


class RoomsManager:
    """Manages multiple game rooms, each with its own GameEngine."""

    def __init__(self):
        """Initialize with a single default room."""
        self.rooms = {}
        self._create_default_room()

    def _create_default_room(self):
        """Create the default room with a fresh GameEngine."""
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
        engine = build_board(board_lines)
        self.rooms["default"] = engine

    def get_room(self, room_id):
        """Get a room by ID, or None if not found."""
        return self.rooms.get(room_id)

    def get_default_room(self):
        """Get the default room."""
        return self.rooms.get("default")

    def list_rooms(self):
        """Return list of all room IDs."""
        return list(self.rooms.keys())

    def room_exists(self, room_id):
        """Check if a room exists."""
        return room_id in self.rooms

    def create_room(self, room_id=None):
        """
        Args:
            room_id: If None, generates a short UUID for readability.
        """
        if room_id is None:
            room_id = str(uuid.uuid4())[:8]
        
        if room_id in self.rooms:
            raise ValueError(f"Room {room_id} already exists")
        
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
        engine = build_board(board_lines)
        self.rooms[room_id] = engine
        return room_id

    def delete_room(self, room_id):
        """Delete a room (cannot delete default room)."""
        if room_id == "default":
            raise ValueError("Cannot delete the default room")
        if room_id not in self.rooms:
            raise ValueError(f"Room {room_id} does not exist")
        del self.rooms[room_id]
