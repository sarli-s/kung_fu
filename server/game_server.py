import asyncio
import time
import websockets
import json
import logging
from server.game.rooms_manager import RoomsManager
from server.protocol.command_parser import MoveValidator, JumpValidator
from server.game.lobby import LobbyManager
from server.network.connection_manager import ConnectionManager
from server.network.broadcaster import Broadcaster
from server.game.event_wirer import EventWirer
from server.network.loop_runner import LoopRunner
from server.protocol.messages import (
    BoardStateMessage, PieceStateSimple, PieceStateMoving,
    MoveResponseMessage, JumpResponseMessage, ErrorMessage, to_json_dict
)

logger = logging.getLogger(__name__)


class GameServer:

    def __init__(self, host="localhost", port=8765, tick_rate_ms=16,
                 broadcast_interval_ms=60, ping_interval_s=30, ping_timeout_s=60):
        self.host = host
        self.port = port
        self.tick_rate_ms = tick_rate_ms
        self.broadcast_interval_ms = broadcast_interval_ms
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
        board = tuple(
            tuple(engine.cell(row, col) for col in range(engine.cols()))
            for row in range(engine.rows())
        )
        states = {}
        for row in range(engine.rows()):
            for col in range(engine.cols()):
                key = f"{row},{col}"
                if engine.is_airborne(row, col):
                    states[key] = to_json_dict(PieceStateSimple(state="airborne"))
                elif engine.is_moving(row, col):
                    cmd = engine.get_move_command(row, col)
                    states[key] = to_json_dict(PieceStateMoving(
                        state="moving",
                        from_row=cmd.from_row, from_col=cmd.from_col,
                        to_row=cmd.to_row, to_col=cmd.to_col,
                        elapsed=cmd.elapsed,
                        checkpoints=tuple(tuple(cp) for cp in cmd.checkpoints),
                    ))
                elif engine.is_short_rest(row, col):
                    states[key] = to_json_dict(PieceStateSimple(state="short_rest"))
                elif engine.is_long_rest(row, col):
                    states[key] = to_json_dict(PieceStateSimple(state="long_rest"))
        color_map = {"w": "white", "b": "black"}
        players = {color_map[p["color"]]: p["username"] for p in self.lobby._rooms.get(room_id, [])}
        scores = {
            "white": engine.move_tracker.get_score("white"),
            "black": engine.move_tracker.get_score("black"),
        }
        elapsed_ms = (time.time() - engine.start_time) * 1000
        msg = BoardStateMessage(
            type="board_state",
            room_id=room_id,
            board=board,
            states=states,
            moves={
                "white": engine.move_tracker.get_moves("white"),
                "black": engine.move_tracker.get_moves("black"),
            },
            players=players,
            game_over=engine.game_over,
            scores=scores,
            elapsed_ms=elapsed_ms,
        )
        return to_json_dict(msg)

    def handle_command(self, room_id, command, player_id=None):
        engine = self.rooms_manager.get_room(room_id)
        if not engine:
            return to_json_dict(ErrorMessage(type="error", success=False, reason="Room not found"))

        cmd_type = command.get("type")
        cmd_data = command.get("data", "")
        player_color = self.lobby.get_color(room_id, player_id) if player_id else None

        def handle_move():
            valid, reason = MoveValidator(engine).execute_move(cmd_data, player_color=player_color)
            return to_json_dict(MoveResponseMessage(type="move_response", success=valid, reason=reason, notation=cmd_data))

        def handle_jump():
            valid, reason = JumpValidator(engine).execute_jump(cmd_data)
            return to_json_dict(JumpResponseMessage(type="jump_response", success=valid, reason=reason, notation=cmd_data))

        handlers = {"move": handle_move, "jump": handle_jump}
        if cmd_type in handlers:
            return handlers[cmd_type]()

        return to_json_dict(ErrorMessage(type="error", success=False, reason=f"Unknown command type: {cmd_type}"))

    # --- public delegates (kept for backward compatibility / monkey-patching) ---

    async def handle_client(self, websocket):
        await self._conn.handle_client(websocket)

    async def broadcast_board_state(self, room_id="default"):
        await self._bcast.broadcast_board_state(room_id)

    async def tick_loop(self):
        await self._loops.tick_loop()

    async def broadcast_loop(self):
        await self._loops.broadcast_loop()

    async def heartbeat_loop(self):
        await self._loops.heartbeat_loop()

    # --- startup ---

    async def start(self):
        tick_task      = asyncio.create_task(self.tick_loop())
        broadcast_task = asyncio.create_task(self.broadcast_loop())
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        async with websockets.serve(self.handle_client, self.host, self.port,
                                    ping_interval=None):
            logger.info(f"Game server started on ws://{self.host}:{self.port}")
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                tick_task.cancel()
                broadcast_task.cancel()
                heartbeat_task.cancel()
                raise


def run_server(host="localhost", port=8765, tick_rate_ms=16):
    logging.basicConfig(level=logging.INFO)
    server = GameServer(host, port, tick_rate_ms)
    asyncio.run(server.start())


if __name__ == "__main__":
    run_server()
