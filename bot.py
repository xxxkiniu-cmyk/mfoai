import os
import time
import requests
from datetime import datetime

key = os.environ.get('OPENROUTER_API_KEY', '')
if not key:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRITICAL: Brak klucza OPENROUTER_API_KEY")
    exit(1)

pytanie = "Podaj krotka motywacyjna wiadomosc na dzis iaj po polsku. Max 2 zdania."

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

if not odpowiedz:
    odpowiedz = "AWARIA: Wszystkie modele AI niedostepne."
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRITICAL: {odpowiedz}")

try:
    requests.post(
        'https://ntfy.sh/centrum-dowodzenia-v3',
        data=odpowiedz.encode('utf-8'),
        headers={'Title': f'MFO.ai | {uzyty_model or "AWARIA"}'},
        timeout=15
    )
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Powiadomienie ntfy wyslane pomyślnie.")
except Exception as e:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad podczas wysylania ntfy: {e}")

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FINISH: Wynik -> {odpowiedz}")
