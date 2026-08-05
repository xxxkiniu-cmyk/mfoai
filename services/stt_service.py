import time
from core.event_bus import EventBus

class STTService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.is_listening = True
        self.session_active = True

    def toggle_listener(self, trace_id: str):
        self.is_listening = not self.is_listening
        status = "active" if self.is_listening else "paused"
        self.event_bus.publish({
            "type": "LISTENER_STATE_CHANGED",
            "payload": {"status": status, "session_active": self.session_active},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "correlation_id": trace_id,
            "source": "stt_service"
        })
        print(f"[INFO] STTService: Nasłuch -> {status}")
