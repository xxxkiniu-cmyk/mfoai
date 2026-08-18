import urllib.request
import json
from core.llm_client import ask
from core.notifier import send
from core.logger import Logger
from core.config import CITY

def get_weather_data():
    try:
        url = "https://wttr.in/" + CITY + "?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                current = data["current_condition"][0]
                temp = current["temp_C"]
                desc = current["weatherDesc"][0]["value"]
                return "Miasto: " + CITY + ", Temperatura: " + temp + "C, Stan: " + desc
    except Exception as e:
        Logger.log("weather", "API", 0.1, "WARNING", error=str(e))
    return "Miasto: " + CITY + ", Dane pogodowe niedostepne."

def run_weather():
    weather_info = get_weather_data()
    prompt = "Na podstawie danych o pogodzie stworz krotkie porady: " + weather_info
    try:
        advice = ask(prompt)
        if not advice or "[ERROR]" in advice:
            raise Exception("LLM offline")
        Logger.log("weather", "LLM", 0.5, "SUCCESS")
    except Exception as e:
        advice = "Pamietaj o dostosowaniu ubioru do pogody!"
        Logger.log("weather", "FALLBACK", 0.1, "WARNING", error=str(e))
    message = weather_info + "\n\nPorada: " + advice
    send("Pogoda: " + CITY, message, priority="default")
    return message

if __name__ == "__main__":
    print(run_weather())


def fetch_weather():
 return run_weather()
