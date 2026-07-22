# KungFu Chess — Local Server Specification

> This document is intended for a coding agent (Amazon Q) that will work on the project.
> It is based on the `CTD 26 – KungFu Chess Server` slide deck, adapted to the actual
> existing code structure of this project.

---

## 1. Where We're Heading (Overview)

Today the game is a **single, local-only process**: `main.py` runs either a textual
input mode (`run.py`) or `--gui` mode that opens a `cv2` window (`gui_mode.py` →
`DisplayLoop`). All the logic (`GameEngine` in `chess/core/session.py`) runs in one
memory space, with no networking at all.

**End goal**: turn this into a local server that lets two players (and later spectators
too) play kung-fu chess against each other over WebSocket, with a login screen, ELO
rating, matchmaking, and rooms — without breaking the existing core (`GameEngine`,
`EngineRules`, `MoveTracker`, etc.).

**Guiding principle**: `GameEngine` stays "dumb" with respect to networking — it will
never know WebSocket exists. All the networking/session/login layers will wrap around
it from the outside, exactly the way `controller.py` today translates text commands
(`click x y`, `jump x y`) into `engine.request_move(...)` calls.

**Order of work**: 6 stages. Each stage stands on its own and should be run and tested
before moving to the next. Do not skip from one stage to the next without the previous
one working end-to-end.

---

## 2. Technical Background — What Already Exists (don't rebuild it!)

| Component | File | Role |
|---|---|---|
| `GameEngine` | `chess/core/session.py` | The core: `request_move`, `request_jump`, `advance(ms)`, emits events |
| `EventEmitter` | `chess/utils/event_emitter.py` | Primitive pub/sub - `subscribe(event, fn)` / `emit(event, **data)` |
| Commands → engine | `chess/core/controller.py` | `COMMAND_HANDLERS`: converts `"click x y"` / `"jump x y"` / `"wait ms"` into engine calls |
| Board building | `chess/services/board_builder.py` | `build_board(board_lines)` → returns a ready `GameEngine` |
| Local rendering | `chess/ui/display.py`, `chess/ui/renderer.py` | Local `cv2` loop - **not** relevant to the server itself |
| Local mouse input | `chess/ui/input_handler.py` | Converts mouse clicks into `controller` commands - should inspire the network protocol |

**Important**: `EventEmitter` already exists and its "core" is good enough. Stage 1
does not build a new Event Bus from scratch — it **extends** it into a server layer
that listens to events and broadcasts them outward.

---

## 3. Detailed Stages

### Stage 0 — Preparation (before anything else)
- Run the existing tests (`python -m pytest tests/`) and confirm a green baseline.
- Create a separate git branch for the server work (e.g. `feature/server`), so the
  local-game `main` branch isn't touched.


### Stage 1 — Bus (extending the existing EventEmitter)
**Goal**: don't build a new pub/sub from scratch — add a layer around the
`EventEmitter` that `GameEngine` already has, so score updates, move logs, sound, and
animations can all "hang off" it.

**Tasks**:
- Create a new module, e.g. `server/game_bus.py`, that takes a `GameEngine` and
  subscribes to `on_move`, `on_capture`, `on_promotion`, `on_game_over` (these events
  already exist in `session.py` — no need to invent new ones at this stage).
- Handlers at this stage can simply `print`/log locally — the goal right now is
  **the registration mechanism**, not yet network broadcasting (that's stage 2).
- Confirm that multiple listeners can be registered for the same event without
  conflict (already supported by `EventEmitter` since `_listeners` is a `list` per
  event).

⚠️ **Warning**: `EventEmitter.emit` today calls listeners synchronously with no
exception handling — if one listener throws, it will halt the entire event chain,
including the board update itself. **Any new listener registered by the server side
must be wrapped in try/except**, so a bug in logging/sound doesn't crash the game.

### Stage 2 — Single-process server + WebSocket
**Goal**: one server process (not multiprocessing/multi-threading to manage the game
itself), holding multiple `GameEngine` instances (one per room), talking to clients
(browser/client) over WebSocket. Establish the room architecture and heartbeat
mechanism from the start.

**Tasks**:
- Choose a WebSocket library (e.g. `websockets` or `python-socketio`) and add it to
  `requirements`/`pyproject`.
- **Design the room structure** as `dict[room_id → GameEngine]` from the start, even
  if only a single `"default"` room exists for now. This avoids a painful refactor
  at stage 6. Each room holds its own `GameEngine` instance.
- Define a **text command protocol**, inspired by the format from the slides
  (`WQe2e5` etc.), mapped to `engine.request_move(from_row, from_col, to_row, to_col)`.
  Decide:
  - Chess coordinates (`e2e5`) vs. raw row/column (like the GUI does today via
    `_pixel_to_cell` with pixels)? Chess coordinates are more readable for an
    external client and are recommended for this stage.
  - Add a new translation layer (parser) — **do not** modify the existing
    `controller.py`, since it's still used by the local GUI mode.
- **Add a move validation wrapper** around `request_move` and `request_jump` that
  returns `(valid: bool, reason: str)` or emits an `on_move_rejected` event. This
  allows the server to tell the client why a move was rejected instead of failing
  silently (see warning below).
- The server loop should call `engine.advance(ms)` at a fixed rate (tick) for each
  room's engine, exactly like the local `DisplayLoop` does today with `delta_ms` —
  just without `cv2`. Broadcast board state to clients as JSON after each tick/move.
  The JSON structure can be based on the existing `board.fmt()` + `board.cell(row, col)`.
- **Implement heartbeat/ping mechanism**: send a ping to each connected client at a
  fixed interval (e.g. every 30 seconds) and expect a pong response. Track the last
  pong time per connection. This allows the server to detect real disconnects faster
  than waiting for the WebSocket library to notice (which can take time). Use this
  for the disconnect detection in stage 5.

⚠️ **Warnings**:
- `GameEngine.request_move` and `request_jump` don't return a value/clear error when
  the request is invalid (they just silently `return` — see `session.py`). The move
  validation wrapper (see task above) must check legality before calling the engine
  and return a reason string so the client knows why the move was rejected.
- Since this is single-process, you **must not** perform blocking I/O calls (e.g.
  reading terminal input for Login in stage 3) inside the same event loop as the
  WebSocket — this will freeze the `advance()` loop for all players. Make sure the
  entire server is async from this stage onward.

### Stage 3 — Home Screen + Login (username only, shell)
**Goal**: per the slides — username-only login (for demo purposes), **in a shell on
the client side**, not GUI. Only two players supported: first to connect = white,
second = black.

**Tasks**:
- Add a "session/lobby" layer on the server side that manages the list of connected
  players and assigns a color (`white`/`black`) by join order.
- **Maintain an explicit player_id → color mapping** on the server side (e.g.
  `{player_id: "w"}` or `{player_id: "b"}`), since `GameEngine` has no concept of
  players — only piece colors. This mapping is per-room and per-connection, not
  persistent yet (persistence comes in stage 4).
- A simple text client (a separate script, not part of `gui_mode.py`) that asks for a
  username and connects over WebSocket.
- A third player trying to connect at this stage should be rejected with a clear
  message (spectator support only arrives in stage 6, via Rooms).

⚠️ **Warning**: there's no persistence yet (that comes in stage 4) — restarting the
server will wipe out all connected players. Document this as a known limitation of
this stage, don't try to "fix it in advance."

### Stage 4 — Password + SQLite + ELO
**Goal**: extend login to include a password stored in SQLite on the server side, and
add an ELO rating starting at 1200.

**Tasks**:
- A `users` table (username, password_hash, elo) in SQLite. **Do not** store passwords
  in plaintext — use hashing (e.g. `bcrypt`/`hashlib` with salt) even if it's "just
  for demo purposes."
- A standard ELO update function (reasonable K-factor, e.g. K=32), triggered by a
  listener on `on_game_over` (the event already exists in `session.py` and includes
  `winner` as a color). **Resolve the winner color back to a player_id** using the
  player_id → color mapping from stage 3, then look up the player's account in the
  users table and update their ELO. This is a natural extension of the Bus from
  stage 1, not a separate mechanism.

⚠️ **Warning**: make sure any SQLite access from the async server doesn't block the
event loop. If using the standard synchronous `sqlite3`, run reads/writes in a thread
pool executor (`loop.run_in_executor`) rather than directly inside an async handler.

### Stage 5 — Play Button + Matchmaking
**Goal**: automatically match players by ELO range ±100, with a one-minute timeout,
and handling of disconnects.

**Tasks**:
- An in-memory queue on the server side of players who "requested Play."
- On each tick / at a fixed interval — check if there are two players in the queue
  whose ELO difference is ≤ 100.
- If no match is found after one minute — send a "no opponent found" message to the
  client.
- A player disconnecting mid-game → automatic resign after 20 seconds, with a
  countdown broadcast to the other client (i.e. requires a server-side timer + a
  "resign countdown" update broadcast via the Bus).

⚠️ **Warning**: detecting a WebSocket "disconnect" isn't always instant (it can take
time for the WebSocket library to notice a `disconnect`). Consider an active
heartbeat/ping to detect real disconnects faster than the 20-second "grace period"
you want to give the player.

### Stage 6 — Rooms (Create / Join / Cancel)
**Goal**: allow creating a room with a unique ID, joining by ID, and supporting
spectators (viewers) from the third joiner onward. Logs on both server and client
side for all activity.

**Tasks**:
- A unique room_id generator (e.g. short UUID / readable 4–6 character code).
- The room structure `dict[room_id → GameEngine]` was already designed in stage 2,
  so this stage extends it: allow clients to create new rooms (generating a new
  room_id) and join existing rooms by ID.
- The second player to join a room = black (per the slides). Anyone joining after
  that = a viewer (read-only — receives state broadcasts but cannot send
  `request_move`).
- **Track a player_role (player vs. viewer) per connection** from the start (even
  though all connections are "player" in stages 2–5). This allows the broadcast
  logic to correctly filter which clients can send moves and which can only observe.
  In stage 6, the third and subsequent joiners will have role = "viewer".
- Logging: for every event (join/move/capture/disconnect), write a line both to a
  file/DB on the server side and broadcast to the client, which writes to its own
  local log.

⚠️ **Note**: the room structure was designed in stage 2 to avoid a painful refactor
here. This stage focuses on the room creation/join logic and viewer support, not on
restructuring the engine storage.

---

## 4. Priority Summary

1. Extended Bus (stage 1) — cheap, doesn't break anything.
2. Server + WebSocket + command protocol + rooms dict + heartbeat (stage 2) — the
   foundation for everything else. Includes move validation wrapper and room
   architecture design.
3. Simple login + player_id → color mapping (stage 3) — needed so there are actually
   "two players" with explicit identity tracking.
4. Password + SQLite + ELO (stage 4) — extends stage 3 with persistence and rating.
5. Matchmaking (stage 5).
6. Rooms + viewer support (stage 6) — extends the room structure from stage 2 with
   creation/join logic and viewer role tracking.

**Do not start stage N+1 before stage N runs end-to-end (you should be able to run
two local clients and see a synchronized move between them).**
