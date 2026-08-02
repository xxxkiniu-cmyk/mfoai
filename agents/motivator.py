import os
import requests

def get_motivation():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"ok": False, "error": "Brak klucza OPENROUTER_API_KEY"}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    models = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free"
    ]
    
    prompt = "Napisz jedno krótkie, mocne, jedozdaniowe hasło motywacyjne na dziś po polsku."

    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                msg = data['choices'][0]['message']['content'].strip()
                return {"ok": True, "model": model, "response": msg}
        except Exception:
            continue

    return {"ok": False, "error": "Wszystkie modele zawiodły"}

def send_notification(message):
    topic = os.getenv("NTFY_TOPIC", "mfoai_bot_alerts")
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=f"💪 Motywacja:\n{message}".encode("utf-8"),
            headers={
                "Title": "MFO.ai - Motivator",
                "Priority": "default"
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
