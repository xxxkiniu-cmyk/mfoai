from core.notifier import send
from core.logger import Logger

def run_summary(results: dict) -> str:
    motivator_res = results.get("motivator", "Brak danych")
    weather_res = results.get("weather", "Brak danych")
    finance_res = results.get("finance", "Brak danych")
    diag_res = results.get("diagnostics", "Brak danych")
    summary_message = (
        f"--- PODSUMOWANIE MFO.ai ---

"
        f"[DIAGNOSTYKA]
{diag_res}

"
        f"[POGODA]
{weather_res}

"
        f"[FINANSE]
{finance_res}

"
        f"[MOTYWACJA]
{motivator_res}"
    )
    try:
        send("MFO.ai: Podsumowanie Dnia", summary_message, priority="default")
        Logger.log("summary", "SYSTEM", 0.2, "SUCCESS")
    except Exception as e:
        Logger.log("summary", "SYSTEM", 0.2, "ERROR", error=str(e))
    return summary_message

if __name__ == "__main__":
    sample = {
        "motivator": "Dzialaj lokalnie, mysl globalnie!",
        "weather": "Temperatura: 20C",
        "finance": "Kursy walut aktualne.",
        "diagnostics": "Wszystkie systemy OK."
    }
    print(run_summary(sample))
