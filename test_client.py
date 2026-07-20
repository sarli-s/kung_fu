"""
Manual integration test client for the KungFu Chess server.

Run the server first:  python -m server.game_server
Then run this script:  python test_client.py
"""

import asyncio
import websockets
import json


async def connect_and_login(uri, username):
    """Connect, login, and return (websocket, color). Raises on failure."""
    ws = await websockets.connect(uri)
    await ws.send(json.dumps({"type": "login", "username": username}))
    resp = json.loads(await ws.recv())
    if resp["type"] != "login_ok":
        await ws.close()
        raise RuntimeError(f"Login failed for {username}: {resp}")
    print(f"  ✓ {username} logged in as {resp['color']}")
    return ws, resp["color"]


async def test_login_and_board_state():
    """Test 1: login receives board_state immediately after."""
    print("\n[Test 1] Login + initial board state")
    uri = "ws://localhost:8765"
    ws, color = await connect_and_login(uri, "alice")
    msg = json.loads(await ws.recv())
    assert msg["type"] == "board_state", f"Expected board_state, got {msg['type']}"
    assert msg["room_id"] == "default"
    print(f"  ✓ Board state received ({len(msg['board'])}x{len(msg['board'][0])})")
    await ws.close()


async def test_two_players_get_different_colors():
    """Test 2: first player = white, second = black."""
    print("\n[Test 2] Two players — color assignment")
    uri = "ws://localhost:8765"
    ws1, color1 = await connect_and_login(uri, "alice")
    ws2, color2 = await connect_and_login(uri, "bob")
    assert color1 == "w" and color2 == "b", f"Expected w/b, got {color1}/{color2}"
    print(f"  ✓ alice={color1}, bob={color2}")
    await ws1.close()
    await ws2.close()


async def test_third_player_rejected():
    """Test 3: third player gets login_error."""
    print("\n[Test 3] Third player rejected")
    uri = "ws://localhost:8765"
    ws1, _ = await connect_and_login(uri, "alice")
    ws2, _ = await connect_and_login(uri, "bob")

    ws3 = await websockets.connect(uri)
    await ws3.send(json.dumps({"type": "login", "username": "charlie"}))
    resp = json.loads(await ws3.recv())
    assert resp["type"] == "login_error", f"Expected login_error, got {resp['type']}"
    print(f"  ✓ charlie rejected: {resp['reason']}")
    await ws3.close()
    await ws1.close()
    await ws2.close()


async def test_move_command():
    """Test 4: send a move command after login."""
    print("\n[Test 4] Move command")
    uri = "ws://localhost:8765"
    ws, _ = await connect_and_login(uri, "alice")
    await ws.recv()  # board_state

    await ws.send(json.dumps({"type": "move", "data": "e2e4"}))
    # Drain until we get a move_response (board_state ticks may arrive first)
    for _ in range(10):
        msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=1.0))
        if msg["type"] == "move_response":
            assert msg["success"] is True, f"Move rejected: {msg['reason']}"
            print(f"  ✓ Move e2e4 accepted")
            break
    await ws.close()


async def main():
    print("=== KungFu Chess Server — Integration Tests ===")
    print("Make sure the server is running: python -m server.game_server")
    try:
        await test_login_and_board_state()
        await test_two_players_get_different_colors()
        await test_third_player_rejected()
        await test_move_command()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise


asyncio.run(main())
