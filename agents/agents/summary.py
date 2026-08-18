from core.notifier import send
from core.logger import Logger
import json, os

def run_summary():
    path = os.path.expanduser("~/.mfo/reports.json")
    try:
        with open(path) as f:
            reports = json.load(f)
        last = reports[-1] if reports else {}
        agents = last.get("agents", {})
        lines = ["📊 Podsumowanie MFO.ai"]
        for name, data in agents.items():
            status = data.get("status", "?")
            icon = "✅" if status == "SUCCESS" else "❌"
            lines.append(f"{icon} {name}: {status}")
        msg = "\n".join(lines)
    except Exception as e:
        msg = f"Podsumowanie: brak danych ({e})"
    Logger.log("summary", "REPORT", 0.1, "SUCCESS")
    send("Podsumowanie MFO.ai", msg)
    return msg

def run():
    return run_summary()

if __name__ == "__main__":
    print(run_summary())
