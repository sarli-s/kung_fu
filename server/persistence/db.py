"""
SQLite persistence layer for users (username, password_hash, elo).

All blocking sqlite3 calls are wrapped in run_in_executor so they
don't block the async event loop.
"""

import asyncio
import sqlite3
import bcrypt
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "users.db"
STARTING_ELO = 1200
ELO_K = 32


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username     TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                elo          INTEGER NOT NULL DEFAULT 1200
            )
        """)
        conn.commit()


_init_db()


# ── sync helpers (run inside executor) ───────────────────────────────────────

def _register(username: str, password: str) -> tuple[bool, str]:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, elo) VALUES (?, ?, ?)",
                (username, hashed, STARTING_ELO),
            )
            conn.commit()
        return True, "registered"
    except sqlite3.IntegrityError:
        return False, "username already taken"


def _verify(username: str, password: str) -> tuple[bool, str]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        return False, "user not found"
    if bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return True, "ok"
    return False, "wrong password"


def _get_elo(username: str) -> int | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT elo FROM users WHERE username = ?", (username,)
        ).fetchone()
    return row["elo"] if row else None


def _update_elos(winner: str, loser: str):
    elo_w = _get_elo(winner) or STARTING_ELO
    elo_l = _get_elo(loser) or STARTING_ELO
    expected_w = 1 / (1 + 10 ** ((elo_l - elo_w) / 400))
    delta = round(ELO_K * (1 - expected_w))
    with _get_conn() as conn:
        conn.execute("UPDATE users SET elo = elo + ? WHERE username = ?", (delta, winner))
        conn.execute("UPDATE users SET elo = elo - ? WHERE username = ?", (delta, loser))
        conn.commit()


# ── async public API ──────────────────────────────────────────────────────────

async def register(username: str, password: str) -> tuple[bool, str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _register, username, password)


async def verify(username: str, password: str) -> tuple[bool, str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _verify, username, password)


async def get_elo(username: str) -> int | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_elo, username)


async def update_elos(winner: str, loser: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _update_elos, winner, loser)
