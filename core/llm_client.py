import urllib.request
import urllib.error
import json
from core.config import OPENROUTER_API_KEY, DEFAULT_MODEL, FALLBACK_MODEL

def ask(prompt):
    try:
        return _make_request(DEFAULT_MODEL, prompt)
    except Exception as e:
        print(f"[WARNING] {e}")
        try:
            return _make_request(FALLBACK_MODEL, prompt)
        except Exception as e2:
            return f"[ERROR] {e2}"

def _make_request(model, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/xxxkiniu-cmyk/mfoai",
        "X-Title": "MFO.ai"
    }
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
