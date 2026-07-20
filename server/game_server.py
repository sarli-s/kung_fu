"""
Game WebSocket server with command protocol and move validation.
"""

import asyncio
import websockets
import json
import logging
from server.rooms_manager import RoomsManager
from server.command_parser import MoveValidator, JumpValidator

logger = logging.getLogger(__name__)


class GameServer:
    """WebSocket server that runs multiple GameEngine instances in rooms."""

    def __init__(self, host="localhost", port=8765, tick_rate_ms=16,
                 ping_interval_s=30, ping_timeout_s=60):
        self.host = host
        self.port = port
        self.tick_rate_ms = tick_rate_ms
        self.ping_interval_s = ping_interval_s
        self.ping_timeout_s = ping_timeout_s
        self.clients = set()
        self.last_pong: dict = {}

        # Initialize rooms manager with default room
        self.rooms_manager = RoomsManager()

    def board_to_json(self, room_id):
        """Convert board state to JSON for a specific room."""
        engine = self.rooms_manager.get_room(room_id)
        if not engine:
            return None
        
        board_data = []
        for row in range(engine.rows()):
            row_data = []
            for col in range(engine.cols()):
                cell = engine.cell(row, col)
                row_data.append(cell)
            board_data.append(row_data)
        
        return {
            "type": "board_state",
            "room_id": room_id,
            "board": board_data,
            "game_over": engine.game_over,
        }

    def handle_command(self, room_id, command):
        engine = self.rooms_manager.get_room(room_id)
        if not engine:
            return {"type": "error", "success": False, "reason": "Room not found"}
        
        cmd_type = command.get("type")
        cmd_data = command.get("data", "")
        
        if cmd_type == "move":
            validator = MoveValidator(engine)
            valid, reason = validator.execute_move(cmd_data)
            return {
                "type": "move_response",
                "success": valid,
                "reason": reason,
                "notation": cmd_data,
            }
        
        elif cmd_type == "jump":
            validator = JumpValidator(engine)
            valid, reason = validator.execute_jump(cmd_data)
            return {
                "type": "jump_response",
                "success": valid,
                "reason": reason,
                "notation": cmd_data,
            }
        
        else:
            return {"type": "error", "success": False, "reason": f"Unknown command type: {cmd_type}"}

    async def handle_client(self, websocket):
        """Handle a single client connection."""
        room_id = "default"
        
        self.clients.add(websocket)
        self.last_pong[websocket] = asyncio.get_event_loop().time()
        logger.info(f"Client connected to room '{room_id}'. Total clients: {len(self.clients)}")
        
        try:
            # Send initial board state
            board_json = self.board_to_json(room_id)
            await websocket.send(json.dumps(board_json))
            
            # Receive and process commands
            async for message in websocket:
                logger.debug(f"Received from client: {message}")
                try:
                    command = json.loads(message)
                    if command.get("type") == "pong":
                        self.last_pong[websocket] = asyncio.get_event_loop().time()
                        continue
                    response = self.handle_command(room_id, command)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "success": False,
                        "reason": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Error handling command: {e}", exc_info=True)
                    await websocket.send(json.dumps({
                        "type": "error",
                        "success": False,
                        "reason": str(e)
                    }))
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.clients.discard(websocket)
            self.last_pong.pop(websocket, None)
            logger.info(f"Client removed. Total clients: {len(self.clients)}")

    async def broadcast_board_state(self):
        """Broadcast current board state to all connected clients."""
        if not self.clients:
            return
        
        room_id = "default"
        board_json = self.board_to_json(room_id)
        message = json.dumps(board_json)
        
        tasks = [client.send(message) for client in self.clients]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def tick_loop(self):
        """Main game loop: advance all room engines and broadcast state.

        Uses a target-timestamp anchor to prevent drift — each tick schedules
        itself relative to when it *should* have fired, not when it actually did.
        Passes real elapsed time to engine.advance() so the engine stays in sync
        with wall time even during catch-up ticks.
        """
        logger.info(f"Tick loop started (tick_rate={self.tick_rate_ms}ms)")
        tick_interval = self.tick_rate_ms / 1000.0
        next_tick = asyncio.get_event_loop().time() + tick_interval
        last_tick = asyncio.get_event_loop().time()

        while True:
            try:
                now = asyncio.get_event_loop().time()
                elapsed_ms = (now - last_tick) * 1000.0
                last_tick = now

                for room_id, engine in self.rooms_manager.rooms.items():
                    engine.advance(elapsed_ms)

                await self.broadcast_board_state()
            except Exception as e:
                logger.error(f"Error in tick loop: {e}", exc_info=True)

            now = asyncio.get_event_loop().time()
            delay = max(0.0, next_tick - now)
            await asyncio.sleep(delay)
            next_tick += tick_interval

    async def heartbeat_loop(self):
        """Send pings to all clients and close stale connections.

        Uses the same loop.time()-anchored scheduling as tick_loop to prevent drift.
        A connection is stale if no pong has been received within ping_timeout_s seconds.
        """
        logger.info(f"Heartbeat loop started (interval={self.ping_interval_s}s, "
                    f"timeout={self.ping_timeout_s}s)")
        loop = asyncio.get_event_loop()
        next_ping = loop.time() + self.ping_interval_s

        while True:
            await asyncio.sleep(max(0.0, next_ping - loop.time()))
            next_ping += self.ping_interval_s
            now = loop.time()

            stale = [ws for ws, t in list(self.last_pong.items())
                     if now - t > self.ping_timeout_s]
            for ws in stale:
                logger.warning("Closing stale connection (no pong received)")
                await ws.close()

            if self.clients:
                ping_msg = json.dumps({"type": "ping"})
                await asyncio.gather(
                    *[ws.send(ping_msg) for ws in self.clients],
                    return_exceptions=True,
                )

    async def start(self):
        """Start the WebSocket server and tick loop."""
        tick_task = asyncio.create_task(self.tick_loop())
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        # ping_interval=None disables the library's built-in ping — our
        # heartbeat_loop is the only disconnect detection mechanism.
        async with websockets.serve(self.handle_client, self.host, self.port,
                                    ping_interval=None):
            logger.info(f"Game server started on ws://{self.host}:{self.port}")
            try:
                await asyncio.Future()  # Run forever
            except asyncio.CancelledError:
                tick_task.cancel()
                heartbeat_task.cancel()
                raise


def run_server(host="localhost", port=8765, tick_rate_ms=16):
    """Convenience function to run the server."""
    logging.basicConfig(level=logging.INFO)
    server = GameServer(host, port, tick_rate_ms)
    asyncio.run(server.start())


if __name__ == "__main__":
    run_server()
