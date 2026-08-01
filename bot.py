import requests
import os

key = os.environ.get("OPENROUTER_KEY")

headers = {
    "Authorization": f"Bearer {key}",
    "HTTP-Referer": "https://github.com/mfoai",
    "X-OpenRouter-Title": "MFO.ai Command Center"
}

MODELE = [
    "google/gemini-2.0-flash-lite-001",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-coder-32b-instruct"
]

pytanie = "Cześć! Podaj krótką, energiczną myśl na dzisiejszy dzień oraz jedną ciekawostkę techniczną. Całość max w 3-4 zdaniach, po polsku."

odpowiedz = None

for model in MODELE:
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": pytanie}]
            },
            timeout=15
        )
        data = r.json()
        if "choices" in data and len(data["choices"]) > 0:
            odpowiedz = data["choices"][0]["message"]["content"]
            print(f"Sukces z modelem: {model}")
            break
        else:
            print(f"Odrzucono przez {model}: {data}")
    except Exception as e:
        print(f"Błąd z modelem {model}: {e}")

if not odpowiedz:
    odpowiedz = "Krytyczny błąd: Wszystkie darmowe modele AI zawiodły!"

requests.post(
    "https://ntfy.sh/centrum-dowodzenia-v3",
    data=odpowiedz.encode("utf-8"),
    headers={"Title": "MFO.ai Poranny Raport"}
)

print("Wysłano powiadomienie ntfy.")
