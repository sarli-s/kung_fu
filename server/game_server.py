import asyncio
import websockets
import json
import logging
from server.rooms_manager import RoomsManager
from server.command_parser import MoveValidator, JumpValidator
from server.lobby import LobbyManager
from server.connection_manager import ConnectionManager
from server.broadcaster import Broadcaster
from server.event_wirer import EventWirer
from server.loop_runner import LoopRunner

logger = logging.getLogger(__name__)


class GameServer:

    def __init__(self, host="localhost", port=8765, tick_rate_ms=16,
                 ping_interval_s=30, ping_timeout_s=60):
        self.host = host
        self.port = port
        self.tick_rate_ms = tick_rate_ms
        self.ping_interval_s = ping_interval_s
        self.ping_timeout_s = ping_timeout_s
        self.clients = set()
        self.last_pong: dict = {}

        self.rooms_manager = RoomsManager()
        self.lobby = LobbyManager()
        self._player_info: dict = {}
        self._buses: dict = {}

        self._conn   = ConnectionManager(self)
        self._bcast  = Broadcaster(self)
        self._wirer  = EventWirer(self)
        self._loops  = LoopRunner(self)

    def board_to_json(self, room_id):
        engine = self.rooms_manager.get_room(room_id)
        if not engine:
            return None
        board_data = []
        for row in range(engine.rows()):
            row_data = []
            for col in range(engine.cols()):
                row_data.append(engine.cell(row, col))
            board_data.append(row_data)
        states = {}
        for row in range(engine.rows()):
            for col in range(engine.cols()):
                if engine.is_airborne(row, col):
                    states[f"{row},{col}"] = {"state": "airborne"}
                elif engine.is_moving(row, col):
                    cmd = engine.get_move_command(row, col)
                    states[f"{row},{col}"] = {
                        "state": "moving",
                        "from_row": cmd.from_row, "from_col": cmd.from_col,
                        "to_row": cmd.to_row, "to_col": cmd.to_col,
                        "elapsed": cmd.elapsed,
                        "checkpoints": cmd.checkpoints,
                    }
                elif engine.is_short_rest(row, col):
                    states[f"{row},{col}"] = {"state": "short_rest"}
                elif engine.is_long_rest(row, col):
                    states[f"{row},{col}"] = {"state": "long_rest"}
        players = {p["color"]: p["username"] for p in self.lobby._rooms.get(room_id, [])}
        return {
            "type": "board_state",
            "room_id": room_id,
            "board": board_data,
            "states": states,
            "moves": {
                "white": engine.move_tracker.moves["white"],
                "black": engine.move_tracker.moves["black"],
            },
            "players": players,
            "game_over": engine.game_over,
        }

    def handle_command(self, room_id, command, player_id=None):
        engine = self.rooms_manager.get_room(room_id)
        if not engine:
            return {"type": "error", "success": False, "reason": "Room not found"}

        cmd_type = command.get("type")
        cmd_data = command.get("data", "")
        player_color = self.lobby.get_color(room_id, player_id) if player_id else None

        if cmd_type == "move":
            valid, reason = MoveValidator(engine).execute_move(cmd_data, player_color=player_color)
            return {"type": "move_response", "success": valid, "reason": reason, "notation": cmd_data}

        if cmd_type == "jump":
            valid, reason = JumpValidator(engine).execute_jump(cmd_data)
            return {"type": "jump_response", "success": valid, "reason": reason, "notation": cmd_data}

        return {"type": "error", "success": False, "reason": f"Unknown command type: {cmd_type}"}

    # --- public delegates (kept for backward compatibility / monkey-patching) ---

    async def handle_client(self, websocket):
        await self._conn.handle_client(websocket)

    async def broadcast_board_state(self, room_id="default"):
        await self._bcast.broadcast_board_state(room_id)

    async def tick_loop(self):
        await self._loops.tick_loop()

    async def heartbeat_loop(self):
        await self._loops.heartbeat_loop()

    # --- startup ---

    async def start(self):
        tick_task      = asyncio.create_task(self.tick_loop())
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        async with websockets.serve(self.handle_client, self.host, self.port,
                                    ping_interval=None):
            logger.info(f"Game server started on ws://{self.host}:{self.port}")
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                tick_task.cancel()
                heartbeat_task.cancel()
                raise


def run_server(host="localhost", port=8765, tick_rate_ms=16):
    logging.basicConfig(level=logging.INFO)
    server = GameServer(host, port, tick_rate_ms)
    asyncio.run(server.start())


if __name__ == "__main__":
    run_server()
