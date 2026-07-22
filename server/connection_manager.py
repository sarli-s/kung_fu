import asyncio
import json
import logging
import websockets

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self, server):
        self.server = server

    async def login_handshake(self, websocket, room_id) -> bool:
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=30)
            msg = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError):
            await websocket.send(json.dumps({"type": "login_error", "reason": "Expected login message"}))
            return False

        if msg.get("type") != "login" or not msg.get("username"):
            await websocket.send(json.dumps({"type": "login_error", "reason": "Expected login message"}))
            return False

        username = msg["username"]
        success, reason, color = self.server.lobby.join(room_id, websocket, username)
        if not success:
            await websocket.send(json.dumps({"type": "login_error", "reason": reason}))
            return False

        self.server._player_info[websocket] = {"username": username, "color": color, "room_id": room_id}
        await websocket.send(json.dumps({"type": "login_ok", "username": username, "color": color}))
        logger.info(f"Player '{username}' joined room '{room_id}' as {color}")
        return True

    async def handle_client(self, websocket):
        room_id = "default"
        self.server.last_pong[websocket] = asyncio.get_event_loop().time()
        logger.info(f"Client connected. Total clients: {len(self.server.clients)}")

        try:
            if not await self.login_handshake(websocket, room_id):
                return

            self.server.clients.add(websocket)

            board_json = self.server.board_to_json(room_id)
            await websocket.send(json.dumps(board_json))

            async for message in websocket:
                logger.debug(f"Received from client: {message}")
                try:
                    command = json.loads(message)
                    if command.get("type") == "pong":
                        self.server._loops.record_pong(websocket)
                        continue
                    response = self.server.handle_command(room_id, command, player_id=websocket)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"type": "error", "success": False, "reason": "Invalid JSON"}))
                except Exception as e:
                    logger.error(f"Error handling command: {e}", exc_info=True)
                    await websocket.send(json.dumps({"type": "error", "success": False, "reason": str(e)}))
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.server.lobby.leave(room_id, websocket)
            self.server._player_info.pop(websocket, None)
            self.server.clients.discard(websocket)
            self.server.last_pong.pop(websocket, None)
            logger.info(f"Client removed. Total clients: {len(self.server.clients)}")
