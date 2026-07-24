import threading
import queue
import asyncio
import json
import sys
import getpass
import websockets
from chess.ui.renderer import BoardRenderer
from chess.ui.display import DisplayLoop
from chess.core.move_tracker import MoveTracker
from chess.entities.move_command import MoveCommand
from server.protocol.command_parser import coords_to_notation


class BoardProxy:
    _ROWS = 8
    _COLS = 8

    def __init__(self, out_q: queue.Queue):
        self._lock = threading.Lock()
        self._board: list[list[str]] = [["." for _ in range(self._COLS)] for _ in range(self._ROWS)]
        self._states: dict[str, dict] = {}
        self._move_cmds: dict[str, MoveCommand] = {}
        self.players: dict[str, str] = {}  # color -> username
        self.game_over = False
        self.scores: dict[str, int] = {"white": 0, "black": 0}
        self.elapsed_ms: float = 0.0
        self.move_tracker = MoveTracker()
        self._out_q = out_q
        self._color: str | None = None
        self._subscribers: dict = {}

    def set_color(self, color: str):
        self._color = color

    def update(self, board, game_over, states=None, moves=None, players=None, scores=None, elapsed_ms=None):
        with self._lock:
            self._board = board
            self._states = states or {}
            self.game_over = game_over
            if moves:
                self.move_tracker.moves["white"] = moves["white"]
                self.move_tracker.moves["black"] = moves["black"]
            if players:
                self.players = players
            if scores:
                self.scores = scores
            if elapsed_ms is not None:
                self.elapsed_ms = elapsed_ms
            # rebuild local MoveCommand objects from server state
            new_cmds = {}
            for key, info in self._states.items():
                if isinstance(info, dict) and info.get("state") == "moving":
                    existing = self._move_cmds.get(key)
                    if existing and existing.to_row == info["to_row"] and existing.to_col == info["to_col"]:
                        # same move already tracked — keep local elapsed (smoother)
                        new_cmds[key] = existing
                    else:
                        cmd = MoveCommand(info["from_row"], info["from_col"], info["to_row"], info["to_col"])
                        cmd.elapsed = info["elapsed"]
                        cmd.checkpoints = [tuple(cp) for cp in info["checkpoints"]]
                        cmd.current_row = info["from_row"]
                        cmd.current_col = info["from_col"]
                        if not hasattr(cmd, "next_idx"):
                            cmd.next_idx = 0
                        new_cmds[key] = cmd
            self._move_cmds = new_cmds
        if game_over:
            for cb in self._subscribers.get("on_game_over", []):
                cb()

    # ── renderer interface ────────────────────────────────────────────────────
    def rows(self): return self._ROWS
    def cols(self): return self._COLS

    def cell(self, row, col):
        with self._lock:
            return self._board[row][col]

    def is_empty(self, row, col):
        return self.cell(row, col) == "."

    def same_color(self, r1, c1, r2, c2):
        t1, t2 = self.cell(r1, c1), self.cell(r2, c2)
        return t1 != "." and t2 != "." and t1[0] == t2[0]

    # ── state methods — always idle; server drives animation ──────────────────
    def is_moving(self, row, col):
        s = self._states.get(f"{row},{col}")
        return isinstance(s, dict) and s.get("state") == "moving"
    def is_airborne(self, row, col):
        s = self._states.get(f"{row},{col}")
        return isinstance(s, dict) and s.get("state") == "airborne"
    def is_short_rest(self, row, col):
        s = self._states.get(f"{row},{col}")
        return isinstance(s, dict) and s.get("state") == "short_rest"
    def is_long_rest(self, row, col):
        s = self._states.get(f"{row},{col}")
        return isinstance(s, dict) and s.get("state") == "long_rest"
    def get_move_command(self, row, col):
        return self._move_cmds.get(f"{row},{col}")

    # ── engine action interface ───────────────────────────────────────────────
    def request_move(self, fr, fc, tr, tc):
        if self._color and self.cell(fr, fc)[0] != self._color:
            return  # ignore moves for opponent's pieces
        notation = coords_to_notation(fr, fc) + coords_to_notation(tr, tc)
        self._out_q.put(json.dumps({"type": "move", "data": notation}))

    def request_jump(self, row, col):
        notation = coords_to_notation(row, col)
        self._out_q.put(json.dumps({"type": "jump", "data": notation}))

    def advance(self, delta_ms):
        with self._lock:
            for cmd in self._move_cmds.values():
                cmd.elapsed += delta_ms

    def subscribe(self, event: str, cb):
        self._subscribers.setdefault(event, []).append(cb)


class ClientGUI:
    def __init__(self, uri: str, username: str, password: str | None = None):
        self.uri = uri
        self.username = username
        self.password = password or ""
        self.out_q: queue.Queue = queue.Queue()
        self.proxy = BoardProxy(self.out_q)
        self.stop_event = threading.Event()
        self._login_event = threading.Event()

    def _start_ws_thread(self):
        def _run():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._ws_loop())
            loop.close()
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return t

    def build_login_payload(self):
        return {"type": "login", "username": self.username, "password": self.password}

    async def _ws_loop(self):
        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(json.dumps(self.build_login_payload()))
                raw = await ws.recv()
                msg = json.loads(raw)
                if msg.get("type") != "login_ok":
                    print(f"Login failed: {msg.get('reason')}")
                    self.stop_event.set()
                    return

                self.proxy.set_color(msg["color"])
                self._login_event.set()

                while not self.stop_event.is_set():
                    while not self.out_q.empty():
                        try:
                            await ws.send(self.out_q.get_nowait())
                        except queue.Empty:
                            break

                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=0.1)
                    except asyncio.TimeoutError:
                        continue

                    msg = json.loads(raw)
                    msg_type = msg.get("type")

                    if msg_type == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                    elif msg_type == "board_state":
                        self.proxy.update(msg["board"], msg.get("game_over", False),
                                          msg.get("states"), msg.get("moves"), msg.get("players"),
                                          msg.get("scores"), msg.get("elapsed_ms"))
                    elif msg_type == "game_over":
                        self.proxy.update(self.proxy._board, True)
                        self.stop_event.set()

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.stop_event.set()

    def run(self):
        ws_thread = self._start_ws_thread()
        self._login_event.wait(timeout=10)
        renderer = BoardRenderer()
        title = f"Kung Fu Chess — {self.username} ({self.proxy._color or '?'})"
        DisplayLoop(self.proxy, renderer, title=title, my_color=self.proxy._color,
                    player_names=self.proxy.players).run()
        self.stop_event.set()
        ws_thread.join(timeout=2)


if __name__ == "__main__":
    uri = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765"
    username = sys.argv[2] if len(sys.argv) > 2 else input("Username: ")
    password = sys.argv[3] if len(sys.argv) > 3 else getpass.getpass("Password: ")
    ClientGUI(uri, username, password).run()
