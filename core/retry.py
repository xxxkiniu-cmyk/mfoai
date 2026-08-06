import time

def retry(func, attempts: int = 3, delay: float = 2.0):
    for i in range(attempts):
        try:
            return func()
        except Exception as e:
            print(f"[RETRY] Próba {i+1}/{attempts} nieudana: {e}")
            if i < attempts - 1:
                time.sleep(delay)
    raise Exception(f"Wszystkie {attempts} próby nieudane")
