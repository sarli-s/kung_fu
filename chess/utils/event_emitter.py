from collections import defaultdict


class EventEmitter:
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event, fn):
        self._listeners[event].append(fn)

    def emit(self, event, **data):
        for fn in self._listeners[event]:
            fn(**data)
