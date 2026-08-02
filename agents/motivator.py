import os
import requests
import time

def get_motivation():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"ok": False, "error": "Brak klucza OPENROUTER_API_KEY"}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/xxxkiniu-cmyk/mfoai",
        "X-Title": "MFO.ai Command Center"
    }
    
    # Aktualna lista niezawodnych modeli darmowych w OpenRouter
    models = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-2-9b-it:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "mistralai/mistral-7b-instruct:free"
    ]
    
    prompt = "Napisz jedno krótkie, zwięzłe i mocne hasło motywacyjne na dziś po polsku. Zwróć wyłącznie treść cytatu, bez komentarzy ani cudzysłowów."

    start_time = time.time()
    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                msg = data['choices'][0]['message']['content'].strip()
                latency = round(time.time() - start_time, 2)
                return {
                    "ok": True, 
                    "model": model, 
                    "latency": f"{latency}s", 
                    "response": msg
                }
        except Exception:
            continue

    return {"ok": False, "error": "Wszystkie modele OpenRouter zawiodły"}

def send_notification(message):
    topic = os.getenv("NTFY_TOPIC", "mfoai_bot_alerts")
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=f"💪 Motywacja dnia:\n{message}".encode("utf-8"),
            headers={
                "Title": "MFO.ai - Motivator",
                "Priority": "default",
                "Tags": "muscle,fire"
            }
        )
    except Exception as e:
        print(f"Błąd wysyłania ntfy: {e}")

def run():
    res = get_motivation()
    if res.get("ok"):
        send_notification(res["response"])
    return res

if __name__ == "__main__":
    print(run())
