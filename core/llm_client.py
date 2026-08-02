import os
import time
import requests
from datetime import datetime

def query_llm(prompt: str) -> dict:
    key = os.environ.get('OPENROUTER_API_KEY', '')
    if not key:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRITICAL: Brak klucza OPENROUTER_API_KEY")
        return {"ok": False, "error": "Brak klucza API"}

    modele = [
        "google/gemma-4-26b-a4b-it:free",
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "openai/gpt-oss-20b:free"
    ]

    for model in modele:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Probuje model: {model}")
            start = time.time()
            
            r = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={'Authorization': f'Bearer {key}'},
                json={
                    'model': model,
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=30
            )
            
            data = r.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content'].strip()
                latency = round(time.time() - start, 2)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: Model {model} (czas: {latency}s)")
                return {
                    "ok": True,
                    "model": model,
                    "latency": latency,
                    "response": content
                }
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: Model {model} zwrocil bledna strukture.")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Blad z {model}: {e}")
            continue

    return {"ok": False, "error": "Wszystkie modele AI z listy fallback sa niedostepne"}
