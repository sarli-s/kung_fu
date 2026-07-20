"""Tests for GameServer with command protocol (stage 2d) and heartbeat (stage 2e)."""

import pytest
import asyncio
import websockets
import json
from server.game_server import GameServer


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_game_server_sends_initial_board_state():
    """Client receives initial board state after login."""
    server = GameServer(host="localhost", port=8772, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8772") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            login_resp = json.loads(await websocket.recv())
            assert login_resp["type"] == "login_ok"

            message = await websocket.recv()
            data = json.loads(message)

            assert data["type"] == "board_state"
            assert data["room_id"] == "default"
            assert "board" in data
            assert data["game_over"] is False
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_game_server_handles_valid_move_command():
    """Server accepts and executes valid move command."""
    server = GameServer(host="localhost", port=8773, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8773") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            await websocket.recv()  # login_ok
            await websocket.recv()  # board_state

            command = {"type": "move", "data": "e2e4"}
            await websocket.send(json.dumps(command))

            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
            data = json.loads(response)

            assert data["type"] == "move_response"
            assert data["success"] is True
            assert data["notation"] == "e2e4"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_game_server_rejects_invalid_move_command():
    """Server rejects invalid move command with reason."""
    server = GameServer(host="localhost", port=8774, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8774") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            await websocket.recv()  # login_ok
            await websocket.recv()  # board_state

            command = {"type": "move", "data": "e4e5"}
            await websocket.send(json.dumps(command))

            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
            data = json.loads(response)

            assert data["type"] == "move_response"
            assert data["success"] is False
            assert data["reason"] == "Move rejected by engine"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_game_server_handles_valid_jump_command():
    """Server accepts and executes valid jump command."""
    server = GameServer(host="localhost", port=8775, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8775") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            await websocket.recv()  # login_ok
            await websocket.recv()  # board_state

            command = {"type": "jump", "data": "e2"}
            await websocket.send(json.dumps(command))

            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
            data = json.loads(response)

            assert data["type"] == "jump_response"
            assert data["success"] is True
            assert data["notation"] == "e2"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_game_server_rejects_invalid_jump_command():
    """Server rejects invalid jump command with reason."""
    server = GameServer(host="localhost", port=8776, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8776") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            await websocket.recv()  # login_ok
            await websocket.recv()  # board_state

            command = {"type": "jump", "data": "e4"}
            await websocket.send(json.dumps(command))

            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
            data = json.loads(response)

            assert data["type"] == "jump_response"
            assert data["success"] is False
            assert data["reason"] == "Jump rejected by engine"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_game_server_handles_invalid_json():
    """Server handles invalid JSON gracefully."""
    server = GameServer(host="localhost", port=8777, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)

    try:
        async with websockets.connect("ws://localhost:8777") as websocket:
            await websocket.send(json.dumps({"type": "login", "username": "alice"}))
            await websocket.recv()  # login_ok
            await websocket.recv()  # board_state

            await websocket.send("not valid json")

            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
            data = json.loads(response)

            assert data["type"] == "error"
            assert data["success"] is False
            assert "JSON" in data["reason"]
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_tick_loop_intervals_consistent_with_slow_broadcast():
    """Tick intervals stay anchored even when broadcast_board_state is slow."""
    server = GameServer(host="localhost", port=8778, tick_rate_ms=50)
    tick_interval = server.tick_rate_ms / 1000.0
    recorded_ticks = []

    async def slow_broadcast():
        recorded_ticks.append(asyncio.get_event_loop().time())
        await asyncio.sleep(tick_interval * 0.8)

    server.broadcast_board_state = slow_broadcast

    task = asyncio.create_task(server.tick_loop())
    await asyncio.sleep(tick_interval * 5.5)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(recorded_ticks) >= 4
    gaps = [recorded_ticks[i + 1] - recorded_ticks[i] for i in range(len(recorded_ticks) - 1)]
    for gap in gaps:
        assert gap < tick_interval * 1.3, f"Gap {gap:.4f}s exceeded 130% of tick interval"


@pytest.mark.asyncio
async def test_tick_loop_advance_uses_real_elapsed_time_during_catchup():
    """engine.advance() receives real elapsed ms, not hardcoded tick_rate_ms.

    During catch-up (delay=0), elapsed_ms reflects actual wall time since last
    tick, preventing the engine from running ahead of real time.
    """
    server = GameServer(host="localhost", port=8779, tick_rate_ms=50)
    tick_interval = server.tick_rate_ms / 1000.0
    advance_calls = []

    for engine in server.rooms_manager.rooms.values():
        original_advance = engine.advance
        def recording_advance(ms, _orig=original_advance):
            advance_calls.append(ms)
            _orig(ms)
        engine.advance = recording_advance

    async def slow_broadcast():
        await asyncio.sleep(tick_interval * 2.0)

    server.broadcast_board_state = slow_broadcast

    task = asyncio.create_task(server.tick_loop())
    await asyncio.sleep(tick_interval * 6)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(advance_calls) >= 2
    for ms in advance_calls[1:]:
        assert ms > server.tick_rate_ms * 0.5, f"advance({ms:.2f}) too small — engine running ahead"
        assert ms < server.tick_rate_ms * 5.0, f"advance({ms:.2f}) too large — elapsed time unreasonable"


@pytest.mark.asyncio
async def test_heartbeat_sends_ping_to_client():
    """Server sends {"type": "ping"} to connected clients after ping interval."""
    server = GameServer(host="localhost", port=8780, tick_rate_ms=50,
                        ping_interval_s=0.1, ping_timeout_s=1.0)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8780") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            await ws.recv()  # login_ok
            await ws.recv()  # initial board state
            deadline = asyncio.get_event_loop().time() + 0.5
            data = {}
            while asyncio.get_event_loop().time() < deadline:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.3)
                data = json.loads(msg)
                if data["type"] == "ping":
                    break
            assert data["type"] == "ping"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_heartbeat_updates_last_pong_on_pong_response():
    """Server updates last_pong time when client sends {"type": "pong"}."""
    server = GameServer(host="localhost", port=8781, tick_rate_ms=50,
                        ping_interval_s=0.1, ping_timeout_s=1.0)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8781") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            await ws.recv()  # login_ok
            await ws.recv()  # initial board state
            client_ws = next(iter(server.clients))
            before = server.last_pong[client_ws]
            await asyncio.sleep(0.05)
            await ws.send(json.dumps({"type": "pong"}))
            await asyncio.sleep(0.05)
            after = server.last_pong[client_ws]
            assert after > before
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_heartbeat_closes_stale_connection():
    """Server closes connection when no pong received within ping_timeout_s."""
    server = GameServer(host="localhost", port=8782, tick_rate_ms=50,
                        ping_interval_s=0.1, ping_timeout_s=0.15)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8782") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            await ws.recv()  # login_ok
            await ws.recv()  # initial board state
            with pytest.raises(websockets.exceptions.ConnectionClosed):
                for _ in range(20):
                    await asyncio.wait_for(ws.recv(), timeout=0.1)
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_heartbeat_does_not_close_responsive_client():
    """Server keeps connection open when client responds to pings."""
    server = GameServer(host="localhost", port=8783, tick_rate_ms=50,
                        ping_interval_s=0.1, ping_timeout_s=0.25)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8783") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            await ws.recv()  # login_ok
            await ws.recv()  # initial board state
            deadline = asyncio.get_event_loop().time() + 0.5
            # Respond to every ping; reaching the deadline without ConnectionClosed
            # proves the server did not close the responsive client.
            while asyncio.get_event_loop().time() < deadline:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.2)
                data = json.loads(msg)
                if data["type"] == "ping":
                    await ws.send(json.dumps({"type": "pong"}))
            assert asyncio.get_event_loop().time() >= deadline
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_login_assigns_white_to_first_player():
    """First player to login gets color 'w'."""
    server = GameServer(host="localhost", port=8784, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8784") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_ok"
            assert resp["color"] == "w"
            assert resp["username"] == "alice"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_login_assigns_black_to_second_player():
    """Second player to login gets color 'b'."""
    server = GameServer(host="localhost", port=8785, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8785") as ws1:
            await ws1.send(json.dumps({"type": "login", "username": "alice"}))
            await ws1.recv()  # login_ok white

            async with websockets.connect("ws://localhost:8785") as ws2:
                await ws2.send(json.dumps({"type": "login", "username": "bob"}))
                resp = json.loads(await ws2.recv())
                assert resp["type"] == "login_ok"
                assert resp["color"] == "b"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_third_player_rejected():
    """Third player receives login_error with 'full' reason."""
    server = GameServer(host="localhost", port=8786, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8786") as ws1:
            await ws1.send(json.dumps({"type": "login", "username": "alice"}))
            await ws1.recv()

            async with websockets.connect("ws://localhost:8786") as ws2:
                await ws2.send(json.dumps({"type": "login", "username": "bob"}))
                await ws2.recv()

                async with websockets.connect("ws://localhost:8786") as ws3:
                    await ws3.send(json.dumps({"type": "login", "username": "charlie"}))
                    resp = json.loads(await ws3.recv())
                    assert resp["type"] == "login_error"
                    assert "full" in resp["reason"].lower()
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_login_error_on_missing_username():
    """Server rejects login with missing username field."""
    server = GameServer(host="localhost", port=8787, tick_rate_ms=50)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8787") as ws:
            await ws.send(json.dumps({"type": "login"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_error"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
