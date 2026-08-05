import os
import requests

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=53.84&longitude=14.62&current=temperature_2m,apparent_temperature,precipitation,weather_code&timezone=auto"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        curr = data.get("current", {})
        temp = curr.get("temperature_2m")
        feels_like = curr.get("apparent_temperature")
        precip = curr.get("precipitation")
        return f"Temp: {temp}°C (odczuwalna: {feels_like}°C) | Opady: {precip} mm"
    except Exception as e:
        return f"Błąd pobierania pogody: {e}"

def send_notification(message):
    topic = os.getenv("NTFY_TOPIC", "mfoai_bot_alerts")
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=f"🌤️ Prognoza Pogody:\n{message}".encode("utf-8"),
            headers={
                "Title": "MFO.ai - Weather Agent",
                "Priority": "default"
            }
        )
    except Exception as e:
        print(f"Błąd wysyłania ntfy: {e}")

if __name__ == "__main__":
    report = fetch_weather()
    print(report)
    send_notification(report)
