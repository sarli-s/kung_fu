import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self, server):
        self.server = server

    def schedule(self, coro):
        def _log_exc(task):
            exc = task.exception()
            if exc:
                logger.error("Broadcast task raised an exception: %s", exc, exc_info=exc)
        task = asyncio.get_event_loop().create_task(coro)
        task.add_done_callback(_log_exc)

    async def _send_all(self, message: str):
        clients = list(self.server.clients)
        results = await asyncio.gather(*[c.send(message) for c in clients], return_exceptions=True)
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                logger.warning("Failed to send to client, removing: %s", result)
                self.server.clients.discard(client)

    async def send_event(self, event: dict):
        if not self.server.clients:
            return
        await self._send_all(json.dumps(event))

    async def broadcast_board_state(self, room_id="default"):
        if not self.server.clients:
            return
        await self._send_all(json.dumps(self.server.board_to_json(room_id)))
