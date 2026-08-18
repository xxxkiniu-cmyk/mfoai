import requests
import os

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM = "Jestes Luna, asystentka MFO AI CENTER. Odpowiadaj zawsze po polsku. Twoj szef to Krzysztof Mazurkiewicz, Master Home Finish Szczecin."

def get_key():
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        try:
            with open(os.path.expanduser("~/.mfo/.env")) as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        key = line.strip().split("=",1)[1]
        except:
            pass
    return key

def ask(prompt, model="google/gemma-3-4b-it"):
    key = get_key()
    r = requests.post(OPENROUTER_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ]}, timeout=30)
    return r.json()["choices"][0]["message"]["content"].strip()
