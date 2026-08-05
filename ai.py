#!/data/data/com.termux/files/usr/bin/python3
# ~/.mfo/ai.py - wywołuje OpenRouter + zapisuje przez save.py
import os, sys, pathlib, requests, json
BASE = pathlib.Path.home() / ".mfo"
ENV = BASE / ".env"

def load_env():
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k,v=line.split("=",1)
                os.environ[k.strip()]=v.strip().strip('"').strip("'")

load_env()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("Brak OPENROUTER_API_KEY w ~/.mfo/.env")
    print("Dodaj: OPENROUTER_API_KEY=sk-or-...")
    sys.exit(1)

PROMPT = " ".join(sys.argv[1:])
if not PROMPT:
    print('Użycie: mfo ai "zrób agenta backup co kopiuje storage co 1h"')
    sys.exit(0)

SYSTEM = """
Jesteś MFO.ai - generator kodu dla Termuxa.
ZASADY BEZ BŁĘDÓW:
1. Każdy plik MUSI zaczynać się od: # FILE: sciezka/wzgledem/~/ 
2. Używaj tylko stdlib + termux-api, zero zewnętrznych lib chyba że user prosi
3. Dodaj py_compile safe code, try/except, mkdir -p logikę
4. Jeden plik = jedna odpowiedzialność
5. Na końcu krótki komentarz jak uruchomić

Format odpowiedzi:
# FILE: agents/backup/agent.py
kod...
# FILE: agents/backup/README.md
...
"""

print(f"⚡ MFO AI myśli: {PROMPT[:80]}...")
resp = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": PROMPT}
        ],
        "temperature": 0.2
    },
    timeout=60
)
data = resp.json()
text = data["choices"][0]["message"]["content"]

# Zapisz przez save.py
tmp = BASE / "storage/inbox/_ai_last.txt"
tmp.write_text(text, encoding="utf-8")
os.system(f"python {BASE}/save.py {tmp}")
print("\n✅ Wygenerowano. Sprawdź: mfo s")

