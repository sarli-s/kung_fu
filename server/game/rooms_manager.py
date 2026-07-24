
import uuid
from chess.services.board_builder import build_board


class RoomsManager:

    def __init__(self):
        self.rooms = {}
        self._create_default_room()

    def _create_default_room(self):
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
        return self.rooms.get(room_id)

    def get_default_room(self):
        return self.rooms.get("default")

    def list_rooms(self):
        return list(self.rooms.keys())

    def room_exists(self, room_id):
        return room_id in self.rooms

    def create_room(self, room_id=None):
        # Short UUID for human-readable room IDs in logs and client URLs
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
        if room_id == "default":
            raise ValueError("Cannot delete the default room")
        if room_id not in self.rooms:
            raise ValueError(f"Room {room_id} does not exist")
        del self.rooms[room_id]
