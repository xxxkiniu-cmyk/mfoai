import os
import json
import requests
from datetime import datetime
from agents.motivator import run_motivator

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] START: Uruchamiam Centrum Dowodzenia AI...")

# Uruchomienie agenta motywacyjnego
result = run_motivator()

# Zapis do pliku reports.json
raport_data = {
    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "status": "SUCCESS" if result.get("ok") else "FAILED",
    "model": result.get("model", "NONE"),
    "latency_sec": result.get("latency", 0),
    "response": result.get("response", result.get("error", "AWARIA"))
}

reports_file = "reports.json"
reports_list = []

if os.path.exists(reports_file):
    try:
        with open(reports_file, 'r', encoding='utf-8') as f:
            reports_list = json.load(f)
    except Exception:
        reports_list = []

reports_list.append(raport_data)

try:
    with open(reports_file, 'w', encoding='utf-8') as f:
        json.dump(reports_list, f, ensure_ascii=False, indent=2)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Raport zapisany w {reports_file}.")
except Exception as e:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad zapisu raportu: {e}")

# Wysyłanie powiadomienia ntfy
if result.get("ok"):
    ntfy_title = f"MFO.ai | {result.get('model')}"
    ntfy_message = f"{result.get('response')}\n\n⏱ Czas odpowiedzi: {result.get('latency')}s"
    ntfy_tags = "robot,rocket"
    ntfy_priority = "3"
else:
    ntfy_title = "MFO.ai | AWARIA"
    ntfy_message = f"Krytyczny błąd: {result.get('error')}"
    ntfy_tags = "warning,rotating_light"
    ntfy_priority = "4"

try:
    requests.post(
        'https://ntfy.sh/centrum-dowodzenia-v3',
        data=ntfy_message.encode('utf-8'),
        headers={
            'Title': ntfy_title,
            'Tags': ntfy_tags,
            'Priority': ntfy_priority
        },
        timeout=15
    )
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Powiadomienie ntfy wyslane pomyslnie.")
except Exception as e:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad wysylania ntfy: {e}")

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FINISH: Cykl zakonczony.")
