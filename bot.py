import requests
import os
import time

key = open(os.path.expanduser('~/.env')).read().strip().split('=')[1]

pytanie = "Podaj krotka motywacyjna wiadomosc na dzisiaj po polsku. Max 2 zdania."

modele = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-20b:free",
    "cohere/north-mini-code:free"
]

odpowiedz = None
uzyty_model = None

for model in modele:
    try:
        print(f"Probuje model: {model}")
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
        if 'choices' in data:
            odpowiedz = data['choices'][0]['message']['content']
            uzyty_model = model
            czas = round(time.time() - start, 1)
            print(f"OK. Model: {model}. Czas: {czas}s")
            break
        else:
            print(f"Blad: {data}")
    except Exception as e:
        print(f"Blad: {e}")
        continue

if not odpowiedz:
    odpowiedz = "AWARIA: Wszystkie modele AI niedostepne."

try:
    requests.post(
        'https://ntfy.sh/centrum-dowodzenia-v3',
        data=odpowiedz.encode('utf-8'),
        headers={'Title': f'MFO.ai | {uzyty_model or "AWARIA"}'},
        timeout=15
    )
except Exception as e:
    print(f"Blad ntfy: {e}")

print("Wyslano:", odpowiedz)
