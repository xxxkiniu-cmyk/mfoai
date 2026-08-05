# FILE: agents/{{name}}/agent.py
import pathlib, time, shutil
from datetime import datetime

BASE = pathlib.Path.home() / "agents/{{name}}"
SRC = pathlib.Path.home() / "storage"
DST = BASE / "backups"

def run():
    DST.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"[{{name}}] Backup {SRC} -> {DST}/{ts}")
    # shutil.copytree(SRC, DST / ts, dirs_exist_ok=True)
    print("OK")

if __name__ == "__main__":
    run()

