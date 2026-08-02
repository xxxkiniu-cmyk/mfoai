import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import motivator, weather, finance

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"=== MFO.ai Command Center [{timestamp}] ===")
    
    report_entry = {
        "timestamp": timestamp,
        "agents": {}
    }
    
    # 1. Agent Motywacyjny
    print("\n[1/3] Uruchamianie Agenta Motywacyjnego...")
    try:
        motiv_res = motivator.run()
        report_entry["agents"]["motivator"] = {
            "status": "SUCCESS" if motiv_res.get("ok") else "FAILED",
            "model": motiv_res.get("model"),
            "latency": motiv_res.get("latency"),
            "response": motiv_res.get("response") or motiv_res.get("error")
        }
    except Exception as e:
        report_entry["agents"]["motivator"] = {"status": "ERROR", "error": str(e)}

    # 2. Agent Pogody
    print("\n[2/3] Uruchamianie Agenta Pogody...")
    try:
        weather_report = weather.fetch_weather()
        weather.send_notification(weather_report)
        report_entry["agents"]["weather"] = {
            "status": "SUCCESS",
            "data": weather_report
        }
    except Exception as e:
        report_entry["agents"]["weather"] = {"status": "ERROR", "error": str(e)}

    # 3. Agent Finansowy
    print("\n[3/3] Uruchamianie Agenta Finansowego...")
    try:
        fin_res = finance.run()
        report_entry["agents"]["finance"] = {
            "status": "SUCCESS" if fin_res.get("ok") else "FAILED",
            "data": f"EUR: {fin_res.get('EUR')}, USD: {fin_res.get('USD')}" if fin_res.get("ok") else fin_res.get("error")
        }
    except Exception as e:
        report_entry["agents"]["finance"] = {"status": "ERROR", "error": str(e)}

    # Zapis do pliku reports.json (Persistence)
    reports_file = "reports.json"
    history = []
    if os.path.exists(reports_file):
        try:
            with open(reports_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(report_entry)

    try:
        with open(reports_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] Zapisano raport do {reports_file}")
    except Exception as e:
        print(f"\n[ERROR] Błąd zapisu raportu: {e}")

if __name__ == "__main__":
    main()
