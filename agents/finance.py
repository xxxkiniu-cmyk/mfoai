import urllib.request
import json
from core.llm_client import ask
from core.notifier import send
from core.logger import Logger

def get_exchange_rates():
    try:
        url = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                rates = data[0]["rates"]
                target = ["USD", "EUR", "GBP"]
                filtered = [f"{r['code']}: {r['mid']} PLN" for r in rates if r['code'] in target]
                return "Kursy NBP:
" + "
".join(filtered)
    except Exception as e:
        Logger.log("finance", "API", 0.1, "WARNING", error=str(e))
    return "Kursy walut niedostepne."

def run_finance():
    rates_info = get_exchange_rates()
    prompt = f"Krotkie podsumowanie kursow walut:
{rates_info}"
    try:
        commentary = ask(prompt)
        if not commentary or "[ERROR]" in commentary:
            raise Exception("LLM offline")
        Logger.log("finance", "LLM", 0.5, "SUCCESS")
    except Exception as e:
        commentary = "Brak komentarza AI. Monitoruj rynki walutowe."
        Logger.log("finance", "FALLBACK", 0.1, "WARNING", error=str(e))
    message = f"{rates_info}

Komentarz: {commentary}"
    send("Finanse: Kursy Walut", message, priority="default")
    return message

if __name__ == "__main__":
    print(run_finance())
