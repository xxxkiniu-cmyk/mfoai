import requests
import os

key = os.environ.get("OPENROUTER_KEY")

pytanie = "Podaj krotka motywacyjna wiadomosc na dzisiaj po polsku. Max 2 zdania."

r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": pytanie}]
    }
)

data = r.json()

if "choices" in data:
    odpowiedz = data["choices"][0]["message"]["content"]
else:
    odpowiedz = "Blad AI: " + str(data)

requests.post(
    "https://ntfy.sh/centrum-dowodzenia-v3",
    data=odpowiedz.encode("utf-8"),
    headers={"Title": "MFO.ai Bot"}
)

print("Wyslano:", odpowiedz)
