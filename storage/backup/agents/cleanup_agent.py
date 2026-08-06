from agents.base_agent import BaseAgent
from core.event_bus import EventBus
import os
import time

class CleanupAgent(BaseAgent):
    def __init__(self, event_bus: EventBus):
        super().__init__("cleanup_agent", event_bus)
        self.log_dir = os.path.expanduser("~/.mfo/storage/logs")
        self.max_age_days = 7

    def run(self):
        self.log("Rozpoczynam czyszczenie")
        removed = 0
        now = time.time()
        for f in os.listdir(self.log_dir):
            path = os.path.join(self.log_dir, f)
            if os.path.isfile(path):
                age = (now - os.path.getmtime(path)) / 86400
                if age > self.max_age_days:
                    os.remove(path)
                    removed += 1
        self.log(f"Usunięto {removed} starych plików")
        self.publish("CLEANUP_DONE", {"removed": removed})
