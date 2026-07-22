"""Unit tests for server/db.py (stage 4 — SQLite + bcrypt + ELO)."""

import pytest
import asyncio
import importlib
from pathlib import Path


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Each test gets its own fresh DB file."""
    import server.db as db_module
    test_db = tmp_path / "test_users.db"
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    # Re-run init so the table is created in the temp DB
    db_module._init_db()
    yield


@pytest.mark.asyncio
async def test_register_new_user():
    import server.db as db
    ok, msg = await db.register("alice", "secret")
    assert ok
    assert msg == "registered"


@pytest.mark.asyncio
async def test_register_duplicate_username():
    import server.db as db
    await db.register("alice", "secret")
    ok, msg = await db.register("alice", "other")
    assert not ok
    assert "taken" in msg


@pytest.mark.asyncio
async def test_verify_correct_password():
    import server.db as db
    await db.register("alice", "secret")
    ok, msg = await db.verify("alice", "secret")
    assert ok
    assert msg == "ok"


@pytest.mark.asyncio
async def test_verify_wrong_password():
    import server.db as db
    await db.register("alice", "secret")
    ok, msg = await db.verify("alice", "wrong")
    assert not ok
    assert "wrong password" in msg


@pytest.mark.asyncio
async def test_verify_unknown_user():
    import server.db as db
    ok, msg = await db.verify("nobody", "x")
    assert not ok
    assert "not found" in msg


@pytest.mark.asyncio
async def test_new_user_starts_at_1200():
    import server.db as db
    await db.register("alice", "secret")
    elo = await db.get_elo("alice")
    assert elo == 1200


@pytest.mark.asyncio
async def test_get_elo_unknown_user_returns_none():
    import server.db as db
    elo = await db.get_elo("nobody")
    assert elo is None


@pytest.mark.asyncio
async def test_update_elos_winner_gains_loser_loses():
    import server.db as db
    await db.register("alice", "a")
    await db.register("bob", "b")
    await db.update_elos(winner="alice", loser="bob")
    elo_alice = await db.get_elo("alice")
    elo_bob = await db.get_elo("bob")
    assert elo_alice > 1200
    assert elo_bob < 1200
    assert elo_alice + elo_bob == 2400  # zero-sum


@pytest.mark.asyncio
async def test_update_elos_equal_players_delta_is_16():
    """Equal ELO players: expected = 0.5, delta = round(32 * 0.5) = 16."""
    import server.db as db
    await db.register("alice", "a")
    await db.register("bob", "b")
    await db.update_elos(winner="alice", loser="bob")
    assert await db.get_elo("alice") == 1216
    assert await db.get_elo("bob") == 1184
