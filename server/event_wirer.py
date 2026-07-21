import logging
from server.game_bus import GameBus
from server.command_parser import coords_to_notation

logger = logging.getLogger(__name__)


class EventWirer:
    def __init__(self, server):
        self.server = server

    def wire(self, room_id):
        engine = self.server.rooms_manager.get_room(room_id)
        bus = GameBus(engine)

        def on_move(**data):
            self.server._bcast.schedule(self.server._bcast.send_event({
                "type": "move", "room_id": room_id,
                "from": coords_to_notation(data["from_row"], data["from_col"]),
                "to":   coords_to_notation(data["to_row"],   data["to_col"]),
                "piece": data.get("piece"),
            }))

        def on_capture(**data):
            self.server._bcast.schedule(self.server._bcast.send_event({
                "type": "capture", "room_id": room_id,
                "square":   coords_to_notation(data["row"], data["col"]),
                "captured": data.get("captured"),
                "by":       data.get("by"),
            }))

        def on_promotion(**data):
            self.server._bcast.schedule(self.server._bcast.send_event({
                "type": "promotion", "room_id": room_id,
                "square": coords_to_notation(data["row"], data["col"]),
                "piece":  data.get("piece"),
            }))

        def on_game_over(**data):
            self.server._bcast.schedule(self.server._bcast.send_event({
                "type": "game_over", "room_id": room_id,
                "winner": data.get("winner"),
            }))

        bus.subscribe("on_move",      "server_broadcast", on_move)
        bus.subscribe("on_capture",   "server_broadcast", on_capture)
        bus.subscribe("on_promotion", "server_broadcast", on_promotion)
        bus.subscribe("on_game_over", "server_broadcast", on_game_over)
        self.server._buses[room_id] = bus
