from core.event_bus import EventBus
from core.logger import log
import time

class BaseAgent:
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus

    def run(self):
        raise NotImplementedError

    def publish(self, event_type: str, payload: dict):
        self.event_bus.publish({
            "type": event_type,
            "payload": payload,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "correlation_id": "",
            "source": self.name
        })

    def log(self, message: str, level: str = "INFO"):
        log(level, self.name, message)
