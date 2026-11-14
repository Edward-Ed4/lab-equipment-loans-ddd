class EventDispatcher:
    """BR5: simple in-process event dispatcher."""

    def __init__(self):
        self._handlers = {}

    def register(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event):
        handlers = self._handlers.get(type(event), [])
        results = []
        for handler in handlers:
            results.append(handler.handle(event))
        return results
