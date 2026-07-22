"""Tests for stage 4 login: register, password verify, elo in login_ok."""

import pytest
import asyncio
import json
import websockets
import server.db as db_module
from server.game_server import GameServer


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_users.db"
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    db_module._init_db()


@pytest.mark.asyncio
async def test_login_without_password_registers_new_user():
    """New user with no password field gets registered and receives login_ok."""
    server = GameServer(host="localhost", port=8800, tick_rate_ms=50)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        async with websockets.connect("ws://localhost:8800") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_ok"
            assert resp["color"] == "w"
            assert resp["elo"] == 1200
    finally:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass


@pytest.mark.asyncio
async def test_login_existing_user_without_password_rejected():
    """Existing user who omits password gets login_error."""
    server = GameServer(host="localhost", port=8801, tick_rate_ms=50)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        # register alice first
        await db_module.register("alice", "secret")
        async with websockets.connect("ws://localhost:8801") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_error"
            assert "password" in resp["reason"].lower()
    finally:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass


@pytest.mark.asyncio
async def test_login_correct_password_accepted():
    """Existing user with correct password gets login_ok with elo."""
    server = GameServer(host="localhost", port=8802, tick_rate_ms=50)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        await db_module.register("alice", "secret")
        async with websockets.connect("ws://localhost:8802") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice", "password": "secret"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_ok"
            assert resp["elo"] == 1200
    finally:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass


@pytest.mark.asyncio
async def test_login_wrong_password_rejected():
    """Existing user with wrong password gets login_error."""
    server = GameServer(host="localhost", port=8803, tick_rate_ms=50)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        await db_module.register("alice", "secret")
        async with websockets.connect("ws://localhost:8803") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice", "password": "wrong"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_error"
            assert "wrong password" in resp["reason"]
    finally:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass


@pytest.mark.asyncio
async def test_login_ok_includes_elo_after_games():
    """login_ok reflects updated ELO after previous games."""
    server = GameServer(host="localhost", port=8804, tick_rate_ms=50)
    task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    try:
        await db_module.register("alice", "secret")
        await db_module.register("bob", "secret")
        await db_module.update_elos(winner="alice", loser="bob")
        async with websockets.connect("ws://localhost:8804") as ws:
            await ws.send(json.dumps({"type": "login", "username": "alice", "password": "secret"}))
            resp = json.loads(await ws.recv())
            assert resp["type"] == "login_ok"
            assert resp["elo"] == 1216
    finally:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass
