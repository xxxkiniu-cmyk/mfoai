import json
import time
import os

LOG_FILE = os.path.expanduser("~/.mfo/storage/logs/mfo.jsonl")

def log(level: str, module: str, message: str, context: dict = {}, correlation_id: str = "", trace_id: str = ""):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level": level,
        "module": module,
        "message": message,
        "context": context,
        "correlation_id": correlation_id,
        "trace_id": trace_id
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{level}] {module}: {message}")
