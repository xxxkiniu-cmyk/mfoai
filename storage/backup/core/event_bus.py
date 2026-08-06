import time

class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: dict):
        event_type = event.get("type")
        for callback in self._subscribers.get(event_type, []):
            callback(event)
        print(f"[EVENT] {event_type} | {event.get('source')} | {event.get('timestamp')}")
