from agents.base_agent import BaseAgent
from core.event_bus import EventBus
import os

class DiagnosticsAgent(BaseAgent):
    def __init__(self, event_bus: EventBus):
        super().__init__("diagnostics_agent", event_bus)

    def run(self):
        self.log("Sprawdzam diagnostykę systemu")
        try:
            with open("/proc/meminfo") as f:
                mem = f.read()
            with open("/proc/loadavg") as f:
                load = f.read().strip()
            stat = os.statvfs(os.path.expanduser("~"))
            storage_free = stat.f_bavail * stat.f_frsize // (1024**3)
            self.log(f"Load: {load} | Storage wolny: {storage_free}GB")
            self.publish("DIAGNOSTICS_DONE", {
                "load": load,
                "storage_free_gb": storage_free
            })
        except Exception as e:
            self.log(f"Błąd diagnostyki: {e}", "ERROR")
