from core.notifier import send
from core.logger import Logger
import urllib.request

def check_internet():
    try:
        urllib.request.urlopen("https://google.com", timeout=5)
        return "OK"
    except:
        return "BRAK"

def run_diagnostics():
    internet = check_internet()
    msg = f"Diagnostyka MFO.ai\nInternet: {internet}"
    Logger.log("diagnostics", "CHECK", 0.1, "SUCCESS")
    send("Diagnostyka MFO.ai", msg)
    return msg

def run():
    return run_diagnostics()

if __name__ == "__main__":
    print(run_diagnostics())
