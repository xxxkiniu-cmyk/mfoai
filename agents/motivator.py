import os
import requests
import time

def get_motivation():
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # 1. Próba z OpenRouter API
    if api_key:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "HTTP-Referer": "https://github.com/xxxkiniu-cmyk/mfoai",
            "X-Title": "MFO.ai Command Center"
        }
        
        models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-2-9b-it:free",
            "qwen/qwen-2.5-72b-instruct:free"
        ]
        
        prompt = "Napisz jedno krótkie, zwięzłe i mocne hasło motywacyjne na dziś po polsku. Zwróć wyłącznie treść cytatu."

        start_time = time.time()
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 80
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=8)
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

    # 2. Niezawodny Fallback (gdy LLM nie odpowie)
    fallback_quotes = [
        "Każdy dzień to nowa szansa na zbudowanie czegoś wielkiego.",
        "Dyscyplina to most między celami a ich osiągnięciem.",
        "Małe postępy każdego dnia sumują się w wielki sukces.",
        "Skup się na procesie, a wyniki przyjdą same.",
        "Nie musisz być wielki, żeby zacząć, ale musisz zacząć, żeby być wielkim."
    ]
    import random
    quote = random.choice(fallback_quotes)
    return {
        "ok": True,
        "model": "fallback-quote-engine",
        "latency": "0.01s",
        "response": quote
    }

def send_notification(message):
    topic = os.getenv("NTFY_TOPIC", "mfoai_bot_alerts")
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=f"💪 Motywacja dnia:\n{message}".encode("utf-8"),
            headers={
                "Title": "MFO.ai - Motivator",
                "Priority": "default",
                "Tags": "fire,muscle"
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
