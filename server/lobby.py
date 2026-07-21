
class LobbyManager:

    def __init__(self):
        # room_id -> list of {"player_id": ws, "username": str, "color": "w"/"b"}
        self._rooms: dict = {}

    def _ensure_room(self, room_id):
        if room_id not in self._rooms:
            self._rooms[room_id] = []

    def join(self, room_id, player_id, username) -> tuple[bool, str, str | None]:
        self._ensure_room(room_id)
        players = self._rooms[room_id]

        if len(players) >= 2:
            return False, "Room is full", None

        color = "w" if len(players) == 0 else "b"
        players.append({"player_id": player_id, "username": username, "color": color})
        return True, "OK", color

    def leave(self, room_id, player_id):
        if room_id not in self._rooms:
            return
        self._rooms[room_id] = [
            p for p in self._rooms[room_id] if p["player_id"] != player_id
        ]

    def get_color(self, room_id, player_id) -> str | None:
        for p in self._rooms.get(room_id, []):
            if p["player_id"] == player_id:
                return p["color"]
        return None

    def player_count(self, room_id) -> int:
        return len(self._rooms.get(room_id, []))
