import time
import threading

class Scheduler:
    def __init__(self):
        self._tasks = []
        self._running = False

    def add(self, func, interval: int, name: str = "task"):
        self._tasks.append({
            "func": func,
            "interval": interval,
            "name": name,
            "last_run": 0
        })

    def start(self):
        self._running = True
        def loop():
            while self._running:
                now = time.time()
                for task in self._tasks:
                    if now - task["last_run"] >= task["interval"]:
                        try:
                            task["func"]()
                            task["last_run"] = now
                        except Exception as e:
                            print(f"[SCHEDULER] {task['name']} błąd: {e}")
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()
        print("[SCHEDULER] Uruchomiony")

    def stop(self):
        self._running = False
        print("[SCHEDULER] Zatrzymany")
