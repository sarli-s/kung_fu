import asyncio
import pytest

import server.event_wirer as ew


class FakeEngine:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_name, callback):
        self.listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name, **data):
        for callback in self.listeners.get(event_name, []):
            callback(**data)


class FakeBroadcaster:
    def __init__(self):
        self.sent = []

    def schedule(self, payload):
        self.sent.append(payload)

    def send_event(self, payload):
        return payload


class FakeRoomsManager:
    def __init__(self, room):
        self._room = room

    def get_room(self, room_id):
        return self._room


class FakeServer:
    def __init__(self, engine):
        self.rooms_manager = FakeRoomsManager(engine)
        self.lobby = type("Lobby", (), {"_rooms": {"room1": [
            {"username": "alice", "color": "w"},
            {"username": "bob", "color": "b"},
        ]}})()
        self._bcast = FakeBroadcaster()
        self._buses = {}


@pytest.mark.asyncio
async def test_game_over_updates_elo_for_winner_and_loser(monkeypatch):
    engine = FakeEngine()
    server = FakeServer(engine)
    wirer = ew.EventWirer(server)

    calls = []

    async def fake_update_elos(winner, loser):
        calls.append((winner, loser))

    monkeypatch.setattr(ew.db, "update_elos", fake_update_elos)

    wirer.wire("room1")
    engine.emit("on_game_over", winner="w")
    await asyncio.sleep(0)

    assert calls == [("alice", "bob")]
