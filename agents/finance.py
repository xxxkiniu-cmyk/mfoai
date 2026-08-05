import requests
import os

def fetch_rates():
    url = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            rates_data = res.json()[0]['rates']
            eur = next((r['mid'] for r in rates_data if r['code'] == 'EUR'), None)
            usd = next((r['mid'] for r in rates_data if r['code'] == 'USD'), None)
            
            return {
                "ok": True,
                "EUR": f"{eur:.4f} PLN" if eur else "N/A",
                "USD": f"{usd:.4f} PLN" if usd else "N/A"
            }
        return {"ok": False, "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_notification(finance_info):
    topic = os.getenv("NTFY_TOPIC", "mfoai_bot_alerts")
    text = f"💶 EUR: {finance_info.get('EUR')}\n💵 USD: {finance_info.get('USD')}"
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=f"📊 Kursy walut (NBP):\n{text}".encode("utf-8"),
            headers={
                "Title": "MFO.ai - Finance",
                "Priority": "low",
                "Tags": "chart_with_upwards_trend,moneybag"
            }
        )
    except Exception as e:
        print(f"Błąd wysyłania ntfy: {e}")

def run():
    info = fetch_rates()
    if info.get("ok"):
        send_notification(info)
    return info

if __name__ == "__main__":
    print(run())
