"""
Game Bus: wraps GameEngine's EventEmitter to safely attach multiple listeners.

GameEngine emits events synchronously with no exception handling — wrapping
listeners in try/except prevents a bug in logging/sound/etc from crashing the game.
"""


class GameBus:

    def __init__(self, engine):
        self.engine = engine
        self._listeners = {}

        # Subscribe to all core events emitted by GameEngine with dispatch methods
        self.engine.subscribe("on_move", self._dispatch_move)
        self.engine.subscribe("on_capture", self._dispatch_capture)
        self.engine.subscribe("on_promotion", self._dispatch_promotion)
        self.engine.subscribe("on_game_over", self._dispatch_game_over)

    def _dispatch_move(self, **data):
        self._dispatch("on_move", **data)

    def _dispatch_capture(self, **data):
        self._dispatch("on_capture", **data)

    def _dispatch_promotion(self, **data):
        self._dispatch("on_promotion", **data)

    def _dispatch_game_over(self, **data):
        self._dispatch("on_game_over", **data)

    def _dispatch(self, event_name, **data):
        if event_name not in self._listeners:
            return
        for listener_name, fn in self._listeners[event_name]:
            try:
                fn(**data)
            except Exception as e:
                print(f"[GameBus] Error in listener '{listener_name}' for event '{event_name}': {e}")

    def subscribe(self, event_name, listener_name, fn):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append((listener_name, fn))
