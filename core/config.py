import os
import json

CONFIG_FILE = os.path.expanduser("~/.mfo/storage/config.json")

DEFAULT = {
    "llm_daily_limit": 60.0,
    "log_level": "INFO",
    "local_first": True,
    "timezone": "Europe/Warsaw"
}

def get(key: str):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            return data.get(key, DEFAULT.get(key))
    return DEFAULT.get(key)

def set(key: str, value):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
    data[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

import os
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
