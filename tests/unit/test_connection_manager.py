import json

import pytest

import server.connection_manager as cm


class FakeWebsocket:
    def __init__(self, message):
        self._messages = [message]
        self.sent = []

    async def recv(self):
        return self._messages.pop(0)

    async def send(self, data):
        self.sent.append(json.loads(data))


class FakeLobby:
    def __init__(self):
        self.calls = []

    def join(self, room_id, player_id, username):
        self.calls.append((room_id, player_id, username))
        return True, "OK", "w"

    def leave(self, room_id, player_id):
        return None


class FakeServer:
    def __init__(self):
        self.lobby = FakeLobby()
        self._player_info = {}
        self.clients = set()
        self.last_pong = {}
        self._loops = type("Loops", (), {"record_pong": lambda self, ws: None})()


@pytest.mark.asyncio
async def test_login_requires_password(monkeypatch):
    manager = cm.ConnectionManager(FakeServer())
    websocket = FakeWebsocket(json.dumps({"type": "login", "username": "alice", "password": ""}))

    called = {"verify": False, "register": False}

    async def fake_verify(*args, **kwargs):
        called["verify"] = True
        return False, "ok"

    async def fake_register(*args, **kwargs):
        called["register"] = True
        return True, "registered"

    monkeypatch.setattr(cm.db, "verify", fake_verify)
    monkeypatch.setattr(cm.db, "register", fake_register)

    ok = await manager.login_handshake(websocket, "default")

    assert ok is False
    assert called["verify"] is False
    assert called["register"] is False
    assert websocket.sent[0]["type"] == "login_error"
    assert "Password is required" in websocket.sent[0]["reason"]


@pytest.mark.asyncio
async def test_login_registers_unknown_user(monkeypatch):
    server = FakeServer()
    manager = cm.ConnectionManager(server)
    websocket = FakeWebsocket(json.dumps({"type": "login", "username": "new_user", "password": "secret"}))

    async def fake_verify(*args, **kwargs):
        return False, "user not found"

    async def fake_register(*args, **kwargs):
        return True, "registered"

    async def fake_get_elo(*args, **kwargs):
        return 1200

    monkeypatch.setattr(cm.db, "verify", fake_verify)
    monkeypatch.setattr(cm.db, "register", fake_register)
    monkeypatch.setattr(cm.db, "get_elo", fake_get_elo)

    ok = await manager.login_handshake(websocket, "default")

    assert ok is True
    assert server.lobby.calls[0][2] == "new_user"
    assert websocket.sent[-1]["type"] == "login_ok"
