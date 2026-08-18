import os, requests
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY")
MODEL = os.getenv("MFO_MODEL", "google/gemma-3-4b-it")
URL = "https://openrouter.ai/api/v1/chat/completions"
def ask(prompt: str) -> str:
    if not OPENROUTER_API_KEY: raise RuntimeError("Brak OPENROUTER_API_KEY")
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/xxxkiniu-cmyk/mfoai", "X-Title": "MFO.ai"}
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    r = requests.post(URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    try: return data["choices"][0]["message"]["content"]
    except: return str(data)
