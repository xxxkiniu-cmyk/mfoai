from agents.base_agent import BaseAgent
from core.event_bus import EventBus

class HealthAgent(BaseAgent):
    def __init__(self, event_bus: EventBus):
        super().__init__("health_agent", event_bus)

    def run(self):
        self.log("Sprawdzam zdrowie systemu")
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                battery = int(f.read().strip())
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp = int(f.read().strip()) // 1000
            self.log(f"Bateria: {battery}% | Temp: {temp}°C")
            self.publish("HEALTH_DONE", {
                "battery": battery,
                "temp_c": temp
            })
        except Exception as e:
            self.log(f"Błąd health: {e}", "ERROR")
