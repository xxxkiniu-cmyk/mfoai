import requests
import os

key = os.environ.get("OPENROUTER_KEY")

headers = {
    "Authorization": f"Bearer {key}",
    "HTTP-Referer": "https://github.com/mfoai",
    "X-OpenRouter-Title": "MFO.ai Command Center"
}

# Pobieranie danych pogodowych
def pobierz_pogode(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe%2FWarsaw"
    try:
        r = requests.get(url, timeout=10)
        return r.json()["daily"]
    except Exception as e:
        return f"Błąd pobierania danych: {e}"

pogoda_miedzyzdroje = pobierz_pogode(53.9284, 14.4460)
pogoda_stargard = pobierz_pogode(53.3386, 15.0387)

pytanie = f"""
Przeanalizuj poniższe dane pogodowe na dzisiaj i przygotuj krótki, czytelny raport na telefon:

Międzyzdroje: {pogoda_miedzyzdroje}
Stargard: {pogoda_stargard}

Zasady:
1. Podaj w zwięzły sposób temperaturę (min/max), wiatr oraz opady dla obu miast.
2. Na koniec dodaj jedno krótkie, mocne i pozytywne zdanie na dobry start dnia.
3. Max 4-5 zdań, czytelny format po polsku.
"""

MODELE = [
    "google/gemini-2.0-flash-lite-001",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-coder-32b-instruct"
]

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
    odpowiedz = "Krytyczny błąd: Nie udało się wygenerować raportu pogodowego!"

requests.post(
    "https://ntfy.sh/centrum-dowodzenia-v3",
    data=odpowiedz.encode("utf-8"),
    headers={"Title": "Poranna Pogoda: Międzyzdroje / Stargard"}
)

print("Wysłano powiadomienie ntfy.")
