import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class LoopRunner:
    def __init__(self, server):
        self.server = server

    def record_pong(self, websocket):
        self.server.last_pong[websocket] = asyncio.get_running_loop().time()

    async def tick_loop(self):
        """Logic-only loop: advances engine state at tick_rate_ms."""
        logger.info(f"Tick loop started (tick_rate={self.server.tick_rate_ms}ms)")
        tick_interval = self.server.tick_rate_ms / 1000.0
        loop = asyncio.get_running_loop()
        next_tick = loop.time() + tick_interval
        last_tick = loop.time()

        for room_id in self.server.rooms_manager.rooms:
            self.server._wirer.wire(room_id)

        while True:
            try:
                now = loop.time()
                elapsed_ms = (now - last_tick) * 1000.0
                last_tick = now
                for engine in self.server.rooms_manager.rooms.values():
                    engine.advance(elapsed_ms)
            except Exception as e:
                logger.error(f"Error in tick loop: {e}", exc_info=True)

            now = loop.time()
            delay = max(0.0, next_tick - now)
            await asyncio.sleep(delay)
            next_tick += tick_interval

    async def broadcast_loop(self):
        """Network loop: sends board state to clients every broadcast_interval_ms."""
        interval = self.server.broadcast_interval_ms / 1000.0
        logger.info(f"Broadcast loop started (interval={self.server.broadcast_interval_ms}ms)")
        loop = asyncio.get_running_loop()
        next_broadcast = loop.time() + interval

        while True:
            await asyncio.sleep(max(0.0, next_broadcast - loop.time()))
            next_broadcast += interval
            try:
                for room_id in self.server.rooms_manager.rooms:
                    await self.server.broadcast_board_state(room_id)
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}", exc_info=True)

    async def heartbeat_loop(self):
        logger.info(f"Heartbeat loop started (interval={self.server.ping_interval_s}s, "
                    f"timeout={self.server.ping_timeout_s}s)")
        loop = asyncio.get_running_loop()
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
