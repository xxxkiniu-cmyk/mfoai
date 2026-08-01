import os
import time
import requests
from datetime import datetime

key = os.environ.get('OPENROUTER_API_KEY', '')
if not key:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRITICAL: Brak klucza OPENROUTER_API_KEY")
    exit(1)

pytanie = "Podaj krotka motywacyjna wiadomosc na dzisiaj po polsku. Max 2 zdania."

modele = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-20b:free"
]

odpowiedz = None
uzyty_model = None
czas_trwania = 0

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] START: Rozpoczynam odpytywanie modeli...")

for model in modele:
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Probuje model: {model}")
        start = time.time()
        
        r = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}'},
            json={
                'model': model,
                'messages': [{'role': 'user', 'content': pytanie}]
            },
            timeout=30
        )
        
        data = r.json()
        if 'choices' in data and len(data['choices']) > 0:
            odpowiedz = data['choices'][0]['message']['content'].strip()
            uzyty_model = model
            czas_trwania = round(time.time() - start, 2)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: Model {model} odpowiedzial w {czas_trwania}s.")
            break
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: Model {model} zwrocil bledna strukture: {data}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad podczas polaczenia z {model}: {e}")
        continue

# Przygotowanie powiadomienia ntfy
if odpowiedz:
    ntfy_title = f"MFO.ai | {uzyty_model}"
    ntfy_message = f"{odpowiedz}\n\n⏱ Czas odpowiedzi: {czas_trwania}s"
    ntfy_tags = "robot,rocket"
    ntfy_priority = "3"  # domyślny
else:
    ntfy_title = "MFO.ai | AWARIA"
    ntfy_message = "Krytyczny błąd: Wszystkie modele AI z listy fallback są niedostępne."
    ntfy_tags = "warning,rotating_light"
    ntfy_priority = "4"  # wysoki priorytet

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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad podczas wysylania ntfy: {e}")

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FINISH: Wynik -> {odpowiedz or ntfy_message}")
