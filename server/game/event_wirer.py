import asyncio
import logging
from server.game.game_bus import GameBus
from server.protocol.command_parser import coords_to_notation
import server.persistence.db as db

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

            winner_color = data.get("winner")
            if not winner_color:
                return

            players = self.server.lobby._rooms.get(room_id, [])
            player_by_color = {p.get("color"): p for p in players if p.get("color")}
            winner_player = player_by_color.get(winner_color)
            loser_player = None
            if winner_color == "w":
                loser_player = player_by_color.get("b")
            elif winner_color == "b":
                loser_player = player_by_color.get("w")

            winner_name = winner_player.get("username") if winner_player else None
            loser_name = loser_player.get("username") if loser_player else None
            if winner_name and loser_name:
                try:
                    asyncio.create_task(db.update_elos(winner_name, loser_name))
                except Exception as exc:
                    logger.exception("Failed to update ELO for game over: %s", exc)

        bus.subscribe("on_move",      "server_broadcast", on_move)
        bus.subscribe("on_capture",   "server_broadcast", on_capture)
        bus.subscribe("on_promotion", "server_broadcast", on_promotion)
        bus.subscribe("on_game_over", "server_broadcast", on_game_over)
        self.server._buses[room_id] = bus
