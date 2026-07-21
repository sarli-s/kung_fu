import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class LoopRunner:
    def __init__(self, server):
        self.server = server

    def record_pong(self, websocket):
        self.server.last_pong[websocket] = asyncio.get_event_loop().time()

    async def tick_loop(self):
        logger.info(f"Tick loop started (tick_rate={self.server.tick_rate_ms}ms)")
        tick_interval = self.server.tick_rate_ms / 1000.0
        next_tick = asyncio.get_event_loop().time() + tick_interval
        last_tick = asyncio.get_event_loop().time()

        # TODO stage 6: remove this loop; wire() moves to room-creation time
        for room_id in self.server.rooms_manager.rooms:
            self.server._wirer.wire(room_id)

        while True:
            try:
                now = asyncio.get_event_loop().time()
                elapsed_ms = (now - last_tick) * 1000.0
                last_tick = now

                for room_id, engine in self.server.rooms_manager.rooms.items():
                    engine.advance(elapsed_ms)

                await self.server.broadcast_board_state()  # dynamic lookup — monkey-patch safe
            except Exception as e:
                logger.error(f"Error in tick loop: {e}", exc_info=True)

            now = asyncio.get_event_loop().time()
            delay = max(0.0, next_tick - now)
            await asyncio.sleep(delay)
            next_tick += tick_interval

    async def heartbeat_loop(self):
        logger.info(f"Heartbeat loop started (interval={self.server.ping_interval_s}s, "
                    f"timeout={self.server.ping_timeout_s}s)")
        loop = asyncio.get_event_loop()
        next_ping = loop.time() + self.server.ping_interval_s

        while True:
            await asyncio.sleep(max(0.0, next_ping - loop.time()))
            next_ping += self.server.ping_interval_s
            now = loop.time()

            stale = [ws for ws, t in list(self.server.last_pong.items())
                     if now - t > self.server.ping_timeout_s]
            for ws in stale:
                logger.warning("Closing stale connection (no pong received)")
                await ws.close()

            if self.server.clients:
                ping_msg = json.dumps({"type": "ping"})
                await asyncio.gather(
                    *[ws.send(ping_msg) for ws in self.server.clients],
                    return_exceptions=True,
                )
